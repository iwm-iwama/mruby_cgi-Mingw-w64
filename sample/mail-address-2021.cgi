#!mruby+cgi.exe
##/usr/bin/mruby+cgi
#coding:utf-8

$VERSION = "Ver.iwm20220626"

=begin

1.入力TSVファイル
	・UTF-8(BOMなし)
	・改行=LF

2.項目
	[0]  char email
	[1]  char 氏名
	[2]  char よみ
	[3]  char 役職
	[4]  int  所属ID
	[5]  char 部名
	[6]  char 課名
	[7]  char 係名
	[8]  int  表示順（管理用／スクリプト側では使用しない）
	[9]  int  勤務先ID（1=本部, 2=地方）
	[10] int  職員種ID（1=職員, 2=非常勤職員）

=end

#---------------------------------------------------------------------
# ユーザ設定
#---------------------------------------------------------------------
# データファイル(TSV)
$IFN = "mail-address-2021.tsv"

# タイトル
$TITLE = "職員メールアドレス検索"

# パンくず
#	[0]title1, [1]url1,
#	[2]title2, [3]url2,
#	..., ...
$ARY_PANKUZU = [
	# Exp, Url
	"パンくず", ""
]

#---------------------------------------------------------------------
# 共通関数
#---------------------------------------------------------------------
#-------------
# URI decode
#-------------
def
IwmRtnUriDecode(
	uri = nil
)
	return uri ? uri.gsub("+", " ").gsub(/%([a-fA-F0-9][a-fA-F0-9])/){$1.hex.chr} : ""
end

#------------------------
# QUERY_STRING analyzer
#------------------------
def
IwmRtnHashQueryString()
	qs = ""

	case ENV['REQUEST_METHOD']
		when "GET"
			qs = ENV['QUERY_STRING']
		when "POST"
			qs = $stdin.read(256) # バイナリ数指定
		else
			return {}
	end

	rtn = {}

	qs.split("&").each do
		|s|
		k, v = s.split("=")
		rtn[k] = IwmRtnUriDecode(v)
	end

	return rtn
end

#---------------------------------------------------------------------
# 共通変数
#---------------------------------------------------------------------
# 検索件数
$SearchCnt = 0

# ?以下のオプション
$UrlQuery = ""

# QUERY_STRING
$hQS = IwmRtnHashQueryString()

#---------------------------------------------------------------------
# keyword : キーワード検索
#---------------------------------------------------------------------
$KEYWORD = $hQS["keyword"]
# 検索用
$_KEYWORD = ($KEYWORD ? $KEYWORD.gsub(/(　| )+/, "\t").gsub("/", "\\/").strip : "")

#---------------------------------------------------------------------
# and_or : AND／OR検索
#---------------------------------------------------------------------
$AND_OR = $hQS["and_or"]
# 検索用／大文字に変換
$_AND_OR = ($AND_OR ? $AND_OR.upcase : "")

#---------------------------------------------------------------------
# org : 所属ID
#---------------------------------------------------------------------
$ORG = $hQS["org"]
# 検索用
$_ORG = ((!$ORG || $ORG == "0") ? "^[1-9][0-9]*" : "^#{$ORG}[0-9]*")

#---------------------------------------------------------------------
# grp1 : 勤務先ID
#---------------------------------------------------------------------
$GRP1 = $hQS["grp1"]
# 検索用
$_GRP1 = ((!$GRP1 || $GRP1 == "0") ? "^[1-9][0-9]*" : "^#{$GRP1}")

#---------------------------------------------------------------------
# grp2 : 職員種ID
#---------------------------------------------------------------------
$GRP2 = $hQS["grp2"]
# 検索用
$_GRP2 = ((!$GRP2 || $GRP2 == "0") ? "^[1-9][0-9]*" : "^#{$GRP2}")

#---------------------------------------------------------------------
# HTMLモジュール
#---------------------------------------------------------------------
def
rtnHtml1Header()
rtn = <<EOD
Content-type:text/html;charset=UTF-8

<!DOCTYPE html>
<html lang="ja">
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<meta http-equiv="Content-Script-Type" content="text/javascript">
<title>#{$TITLE}</title>
<style type="text/css">
@charset "utf-8";
body
{
	background:#fefefe;
	font-family:sans-serif;
	margin:0;
	margin-left:auto;
	margin-right:auto;
	padding:10px 0;
	width:800px;
}
a[href]
{
	text-decoration:none;
}
a[name]
{
	color:transparent;
	font-size:15px;
}
a[name]:hover
{
	opacity:0;
}
a:hover
{
	background:rgba(255, 255, 0, 0.6);
	text-decoration:none;
}
font._a1
{
	color:#000;
	font-size:26px;
	line-height:1.0;
	margin:0;
	padding:0;
}
font._a2
{
	color:#ffa000;
	font-size:14px;
	margin:0;
	padding:0;
}
font._a3
{
	color:#6b72fa;
	font-size:14px;
	margin:0;
	padding:0;
}
font._a4
{
	font-size:12px;
	margin:0;
	padding:0;
}
table
{
	border-collapse:collapse;
	border:0;
	font-size:12px;
	width:100%;
}
th
{
	background:#777;
	border:solid 1px #555;
	color:#fff;
	font-weight:500;
	padding:0 8px;
	text-align:center;
}
td
{
	background:#fff;
	border:solid 1px #555;
	margin:0;
	padding:0 4px;
}
td._quickLink
{
	background-color:transparent;
	border:solid 0;
	margin:0;
	padding:4px 0;
}
input[type=text]
{
	background:#fff;
	border:solid 1px #ffa000;
	font-size:14px;
	height:19px;
	/* ime-mode:active; */
	margin:0 0 0 4px;
	padding:0 5px;
	vertical-align:top;
	width:160px;
}
select
{
	background:#ffa000;
	border:solid 1px #ffa000;
	color:#fff;
	height:21px;
	margin:0;
	padding:0;
}
select:hover
{
	box-shadow:0 0 0 0;
	color:#000;
}
option
{
	background:#fff;
	border:0;
	color:#000;
}
input#button_init
{
	background:#ffa000;
	border:solid 1px #ffa000;
	color:#fff;
	height:21px;
	margin:0;
	padding:0 6px 0 2px;
	vertical-align:top;
}
input#button_init:hover
{
	box-shadow:0 0 0 0;
	color:#000;
}
input[type=button]
{
	background:#3d7cce;
	border:0;
	color:#fff;
	height:21px;
	margin:0;
	padding:0 14px 2px 14px;
}
input[type=button]:hover
{
	box-shadow:0 0 2px 1px #ff0;
}
textarea
{
	background:#fff;
	border:solid 1px #555;
	font-size:11px;
	padding:4px;
}
textarea#_textarea11
{
	height:60px;
	width:450px;
}
ul, li
{
	list-style:none;
}
div._boxExplain
{
	background:#fff;
	border:solid 1px #f00;
	box-shadow:0 0 3px 3px #eee;
	border-radius:8px;
	line-height:0.7;
	margin:0 4px;
	padding:10px;
	width:630px;
}
div._boxExplain font._c1
{
	color:#00f;
	font-size:15px;
	line-height:1.0;
}
div._boxExplain font._c2
{
	font-size:12px;
	font-weight:600;
	line-height:1.0;
	margin-left:12px;
}
div._boxExplain font._c3
{
	color:#f00;
	font-size:12px;
	line-height:1.0;
	margin-left:12px;
}
div._boxExplain font._c4
{
	font-family:monospace;
	font-size:12px;
	line-height:1.0;
	margin-left:12px;
}
div._v2px
{
	margin-top:2px;
}
div._v4px
{
	margin-top:4px;
}
div._v6px
{
	margin-top:6px;
}
div._v10px
{
	margin-top:10px;
}
div._v20px
{
	margin-top:20px;
}
div._v200px
{
	margin-top:200px;
}
div._hurigana
{
	color:#3d7cce;
	font-size:9px;
	margin:0;
	padding:0;
}
/*--------------------------------------------------------------------
	z-index:502
	Balloon Help
--------------------------------------------------------------------*/
ul._balloon
{
	float:left;
	font-family:monospace;
	list-style:none;
	margin:0;
	padding:0;
	position:relative;
	z-index:502;
}
ul._balloon ul
{
	visibility:hidden;
}
ul._balloon li:hover > ul
{
	visibility:visible;
}
ul._balloon li span
{
	background:#fff;
	border:1px solid #ffa000;
	box-shadow:0 0 3px 3px #eee;
	color:#000;
	font-size:12px;
	font-weight:600;
	left:12px;
	line-height:1.2;
	margin:0;
	padding:6px 8px 10px 8px;
	position:absolute;
	text-align:left;
	top:30px;
	width:500px;
}
ul._balloon li span:after
{
	content:"";
	border-bottom:14px solid #ffa000;
	border-left:7px solid transparent;
	border-right:7px solid transparent;
	left:2px;
	position:absolute;
	top:-14px;
}
ul._balloon li span font._b1
{
	color:#f00;
	font-size:14px;
	line-height:1.5;
}
ul._balloon li span font._b2
{
	color:#000;
	font-size:12px;
	margin-left:12px;
	line-height:1.5;
}
/*--------------------------------------------------------------------
	Horizontal CSS Drop-Down Menu Module
	@file      dropdown.css
	@package   Dropdown
	@version   0.8
	@type      Transitional
	@stacks    -600
	@browsers  Windows:IE6+,Opera7+,Firefox1+,Mac OS:Safari2+,Firefox2+
	@link      http://www.lwis.net/
	@copyright 2006-2008 Live Web Institute
--------------------------------------------------------------------*/
ul._dropdown,
ul._dropdown li,
ul._dropdown ul
{
	float:left;
	font-size:12px;
	list-style:none;
	z-index:600;
}
ul._dropdown
{
	position:relative;
	margin:0;
	padding:0;
}
ul._dropdown a
{
	display:block;
}
ul._dropdown ul
{
	background:#00a46c;
	border:solid 1px #00a46c;
	margin:-1px 0 0 0;
	padding:0;
	position:absolute;
	top:100%;
	visibility:hidden;
	width:180px;
}
ul._dropdown ul a
{
	padding:2px 6px;
}
ul._dropdown li
{
	background:#fff;
	margin:0 0 0 4px;
	padding:0;
}
ul._dropdown li:hover
{
	background:#ff0;
	position:relative;
}
ul._dropdown li:hover > ul
{
	visibility:visible;
}
ul._dropdown li a._top
{
	background:#00a46c;
	color:#fff;
	margin:0;
	padding:3px 14px;
}
ul._dropdown li a._top:hover
{
	box-shadow:0 0 2px 1px #ff0;
}
ul._dropdown ul ul
{
	left:120px;
	top:0;
}
ul._dropdown ul li
{
	float:none;
}
ul._dropdown li li
{
	border:solid 1px #fafafa;
}
/*--------------------------------------------------------------------
	z-index:599
	1列目
--------------------------------------------------------------------*/
ul._dropdown1
{
	z-index:599;
}
</style>
</head>
<body>
EOD
	return rtn
end

def
rtnHtml2PageHeader()
rtn = <<EOD
<a name=\"0\">#0</a>
<br>
<font class="_a4">
EOD
	i1 = $ARY_PANKUZU.size
	i2 = 0
	while i2 < i1
		rtn << "<a href=\"#{$ARY_PANKUZU[i2 + 1]}\" target=\"_self\">#{$ARY_PANKUZU[i2]}</a>&nbsp;&gt;&nbsp;"
		i2 += 2
	end
rtn << <<EOD
</font>
<div class="_v10px"></div>
<font class="_a1">#{$TITLE}</font>
<div class="_v10px"></div>
EOD
	return rtn
end

def
rtnHtml2PageSearch()
	sSelectAndOr = ""

	["AND", "OR", "NOR"].each do
		|s|
		sSelectAndOr << "<option"
		if s == $_AND_OR
			sSelectAndOr << " selected"
		end
		sSelectAndOr << " value=\"#{s}\">#{s}</option>"
	end

rtn = <<EOD
<table>
 <tr>
  <td class="_quickLink">
   <ul class="_dropdown _dropdown1">
    <li>
     <a class="_top" href="javascript:wGrp1('1')">▼本部</a>
     <ul>
      <li>
       <a href="javascript:wOrg('22')">企画部</a>
       <ul>
        <li><a href="javascript:wOrg('220')">部</a></li>
        <li>
         <a href="javascript:wOrg('221')">企画調整課</a>
         <ul>
          <li><a href="javascript:wOrg('2210')">課</a></li>
          <li><a href="javascript:wOrg('2211')">総務係</a></li>
          <li><a href="javascript:wOrg('2212')">管理係</a></li>
          <li><a href="javascript:wOrg('2213')">企画係</a></li>
          <li><a href="javascript:wOrg('2214')">企画調整係</a></li>
          <li><a href="javascript:wOrg('2215')">研究調整係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('222')">技術管理課</a>
         <ul>
          <li><a href="javascript:wOrg('2220')">課</a></li>
          <li><a href="javascript:wOrg('2221')">技術管理係</a></li>
          <li><a href="javascript:wOrg('2222')">基準係</a></li>
          <li><a href="javascript:wOrg('2223')">国際標準係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('223')">測量指導課</a>
         <ul>
          <li><a href="javascript:wOrg('2230')">課</a></li>
          <li><a href="javascript:wOrg('2231')">技術振興係</a></li>
          <li><a href="javascript:wOrg('2232')">統計調査係</a></li>
          <li><a href="javascript:wOrg('2233')">公共測量係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('224')">国際課</a>
         <ul>
          <li><a href="javascript:wOrg('2240')">課</a></li>
          <li><a href="javascript:wOrg('2241')">国際企画係</a></li>
          <li><a href="javascript:wOrg('2242')">国際連携調整係</a></li>
          <li><a href="javascript:wOrg('2243')">国際協力係</a></li>
          <li><a href="javascript:wOrg('2244')">研究交流係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('225')">地理空間情報企画室</a>
         <ul>
          <li><a href="javascript:wOrg('2250')">室</a></li>
          <li><a href="javascript:wOrg('2251')">情報政策係</a></li>
          <li><a href="javascript:wOrg('2252')">計画調整係</a></li>
          <li><a href="javascript:wOrg('2253')">地理情報システム係</a></li>
          <li><a href="javascript:wOrg('2254')">普及指導係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('226')">防災推進室</a>
         <ul>
          <li><a href="javascript:wOrg('2260')">室</a></li>
          <li><a href="javascript:wOrg('2261')">防災管理係</a></li>
          <li><a href="javascript:wOrg('2262')">防災調整係</a></li>
          <li><a href="javascript:wOrg('2263')">防災調査係</a></li>
         </ul>
        </li>
       </ul>
      </li>
      <li>
       <a href="javascript:wOrg('31')">測地部</a>
       <ul>
        <li><a href="javascript:wOrg('310')">部</a></li>
        <li>
         <a href="javascript:wOrg('311')">計画課</a>
         <ul>
          <li><a href="javascript:wOrg('3110')">課</a></li>
          <li><a href="javascript:wOrg('3111')">総務係</a></li>
          <li><a href="javascript:wOrg('3112')">管理係</a></li>
          <li><a href="javascript:wOrg('3113')">計画第一係</a></li>
          <li><a href="javascript:wOrg('3114')">計画第二係</a></li>
          <li><a href="javascript:wOrg('3115')">技術管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('312')">測地基準課</a>
         <ul>
          <li><a href="javascript:wOrg('3120')">課</a></li>
          <li><a href="javascript:wOrg('3121')">調査係</a></li>
          <li><a href="javascript:wOrg('3122')">測地標準係</a></li>
          <li><a href="javascript:wOrg('3123')">基準係</a></li>
          <li><a href="javascript:wOrg('3124')">基準管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('313')">物理測地課</a>
         <ul>
          <li><a href="javascript:wOrg('3130')">課</a></li>
          <li><a href="javascript:wOrg('3131')">調査係</a></li>
          <li><a href="javascript:wOrg('3132')">地磁気係</a></li>
          <li><a href="javascript:wOrg('3133')">重力係</a></li>
          <li><a href="javascript:wOrg('3134')">ジオイド係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('314')">宇宙測地課</a>
         <ul>
          <li><a href="javascript:wOrg('3140')">課</a></li>
          <li><a href="javascript:wOrg('3141')">調査係</a></li>
          <li><a href="javascript:wOrg('3142')">基線解析係</a></li>
          <li><a href="javascript:wOrg('3143')">超長基線係</a></li>
          <li><a href="javascript:wOrg('3144')">地球変動観測係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('315')">機動観測課</a>
         <ul>
          <li><a href="javascript:wOrg('3150')">課</a></li>
          <li><a href="javascript:wOrg('3151')">調査係</a></li>
          <li><a href="javascript:wOrg('3152')">強化観測係</a></li>
          <li><a href="javascript:wOrg('3153')">火山観測係</a></li>
          <li><a href="javascript:wOrg('3154')">機動観測係</a></li>
          <li><a href="javascript:wOrg('3155')">応用測地係</a></li>
         </ul>
        </li>
       </ul>
      </li>
      <li>
       <a href="javascript:wOrg('34')">地理空間情報部</a>
       <ul>
        <li><a href="javascript:wOrg('340')">部</a></li>
        <li>
          <a href="javascript:wOrg('341')">企画調査課</a>
         <ul>
          <li><a href="javascript:wOrg('3410')">課</a></li>
          <li><a href="javascript:wOrg('3411')">総務係</a></li>
          <li><a href="javascript:wOrg('3412')">管理係</a></li>
          <li><a href="javascript:wOrg('3413')">計画第一係</a></li>
          <li><a href="javascript:wOrg('3414')">計画第二係</a></li>
          <li><a href="javascript:wOrg('3415')">技術管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('342')">情報企画課</a>
         <ul>
          <li><a href="javascript:wOrg('3420')">課</a></li>
          <li><a href="javascript:wOrg('3421')">調査係</a></li>
          <li><a href="javascript:wOrg('3422')">情報企画係</a></li>
          <li><a href="javascript:wOrg('3423')">連携調整係</a></li>
          <li><a href="javascript:wOrg('3424')">ワンストップサービス係</a></li>
          <li><a href="javascript:wOrg('3425')">審査係</a></li>
          <li><a href="javascript:wOrg('3426')">提供普及係</a></li>
          <li><a href="javascript:wOrg('3427')">活用調査係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('343')">情報サービス課</a>
         <ul>
          <li><a href="javascript:wOrg('3430')">課</a></li>
          <li><a href="javascript:wOrg('3431')">調査係</a></li>
          <li><a href="javascript:wOrg('3432')">地理史料係</a></li>
          <li><a href="javascript:wOrg('3433')">測量成果係</a></li>
          <li><a href="javascript:wOrg('3434')">地図成果係</a></li>
          <li><a href="javascript:wOrg('3435')">公共測量成果保管係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('344')">情報普及課</a>
         <ul>
          <li><a href="javascript:wOrg('3440')">課</a></li>
          <li><a href="javascript:wOrg('3441')">調査係</a></li>
          <li><a href="javascript:wOrg('3442')">ウェブシステム係</a></li>
          <li><a href="javascript:wOrg('3443')">ネットワーク技術係</a></li>
          <li><a href="javascript:wOrg('3444')">調整係</a></li>
          <li><a href="javascript:wOrg('3445')">地図作成技術係</a></li>
          <li><a href="javascript:wOrg('3446')">応用技術係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('345')">情報システム課</a>
         <ul>
          <li><a href="javascript:wOrg('3450')">課</a></li>
          <li><a href="javascript:wOrg('3451')">情報処理係</a></li>
          <li><a href="javascript:wOrg('3452')">システム開発係</a></li>
          <li><a href="javascript:wOrg('3453')">情報セキュリティ係</a></li>
         </ul>
        </li>
       </ul>
      </li>
      <li>
       <a href="javascript:wOrg('36')">基本図情報部</a>
       <ul>
        <li><a href="javascript:wOrg('360')">部</a></li>
        <li>
         <a href="javascript:wOrg('361')">管理課</a>
         <ul>
          <li><a href="javascript:wOrg('3610')">課</a></li>
          <li><a href="javascript:wOrg('3611')">総務係</a></li>
          <li><a href="javascript:wOrg('3612')">管理係</a></li>
          <li><a href="javascript:wOrg('3613')">計画第一係</a></li>
          <li><a href="javascript:wOrg('3614')">計画第二係</a></li>
          <li><a href="javascript:wOrg('3615')">技術管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('362')">国土基本情報課</a>
         <ul>
          <li><a href="javascript:wOrg('3620')">課</a></li>
          <li><a href="javascript:wOrg('3621')">調査係</a></li>
          <li><a href="javascript:wOrg('3622')">調整係</a></li>
          <li><a href="javascript:wOrg('3623')">データベース係</a></li>
          <li><a href="javascript:wOrg('3624')">基盤地図情報係</a></li>
          <li><a href="javascript:wOrg('3625')">国土基本情報第一係</a></li>
          <li><a href="javascript:wOrg('3626')">国土基本情報第二係</a></li>
          <li><a href="javascript:wOrg('3627')">国土広域情報係</a></li>
          <li><a href="javascript:wOrg('3628')">技術管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('363')">基本図課</a>
         <ul>
          <li><a href="javascript:wOrg('3630')">課</a></li>
          <li><a href="javascript:wOrg('3631')">調査係</a></li>
          <li><a href="javascript:wOrg('3632')">基本図第一係</a></li>
          <li><a href="javascript:wOrg('3633')">基本図第二係</a></li>
          <li><a href="javascript:wOrg('3634')">技術管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('364')">地名情報課</a>
         <ul>
          <li><a href="javascript:wOrg('3640')">課</a></li>
          <li><a href="javascript:wOrg('3641')">調査係</a></li>
          <li><a href="javascript:wOrg('3642')">基本情報調査係</a></li>
          <li><a href="javascript:wOrg('3643')">行政区画係</a></li>
          <li><a href="javascript:wOrg('3644')">地名情報係</a></li>
          <li><a href="javascript:wOrg('3645')">地理識別子係</a></li>
          <li><a href="javascript:wOrg('3646')">技術管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('365')">画像調査課</a>
         <ul>
          <li><a href="javascript:wOrg('3650')">課</a></li>
          <li><a href="javascript:wOrg('3651')">調査係</a></li>
          <li><a href="javascript:wOrg('3652')">機動撮影係</a></li>
          <li><a href="javascript:wOrg('3653')">応用調査係</a></li>
          <li><a href="javascript:wOrg('3654')">写真図係</a></li>
          <li><a href="javascript:wOrg('3655')">画像データベース係</a></li>
          <li><a href="javascript:wOrg('3656')">三次元地理情報係</a></li>
          <li><a href="javascript:wOrg('3657')">技術管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('366')">地図情報技術開発室</a>
         <ul>
          <li><a href="javascript:wOrg('3660')">室</a></li>
          <li><a href="javascript:wOrg('3661')">調査係</a></li>
          <li><a href="javascript:wOrg('3662')">技術開発第一係</a></li>
          <li><a href="javascript:wOrg('3663')">技術開発第二係</a></li>
          <li><a href="javascript:wOrg('3664')">技術開発第三係</a></li>
         </ul>
        </li>
       </ul>
      </li>
      <li>
       <a href="javascript:wOrg('38')">応用地理部</a>
       <ul>
        <li><a href="javascript:wOrg('380')">部</a></li>
        <li>
         <a href="javascript:wOrg('381')">企画課</a>
         <ul>
          <li><a href="javascript:wOrg('3810')">課</a></li>
          <li><a href="javascript:wOrg('3811')">総務係</a></li>
          <li><a href="javascript:wOrg('3812')">管理係</a></li>
          <li><a href="javascript:wOrg('3813')">企画第一係</a></li>
          <li><a href="javascript:wOrg('3814')">企画第二係</a></li>
          <li><a href="javascript:wOrg('3815')">技術管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('382')">環境地理課</a>
         <ul>
          <li><a href="javascript:wOrg('3820')">課</a></li>
          <li><a href="javascript:wOrg('3821')">管理係</a></li>
          <li><a href="javascript:wOrg('3822')">環境地理情報調査係</a></li>
          <li><a href="javascript:wOrg('3823')">国土環境モニタリング係</a></li>
          <li><a href="javascript:wOrg('3824')">地球地図整備係</a></li>
          <li><a href="javascript:wOrg('3825')">湖沼湿原調査係</a></li>
          <li><a href="javascript:wOrg('3826')">土地利用情報係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('383')">防災地理課</a>
         <ul>
          <li><a href="javascript:wOrg('3830')">課</a></li>
          <li><a href="javascript:wOrg('3831')">管理係</a></li>
          <li><a href="javascript:wOrg('3832')">土地条件調査係</a></li>
          <li><a href="javascript:wOrg('3833')">活断層情報係</a></li>
          <li><a href="javascript:wOrg('3834')">防災地理情報係</a></li>
          <li><a href="javascript:wOrg('3835')">災害地理調査係</a></li>
          <li><a href="javascript:wOrg('3836')">火山調査係</a></li>
          <li><a href="javascript:wOrg('3837')">災害対策地理情報係</a></li>
         </ul>
        </li>
       </ul>
      </li>
     </ul>
    </li>
    <li>
     <a class="_top" href="javascript:wGrp1('2')">▼地方</a>
     <ul>
      <li>
       <a href="javascript:wOrg('61')">北海道</a>
       <ul>
        <li><a href="javascript:wOrg('610')">部</a></li>
        <li>
         <a href="javascript:wOrg('611')">管理課</a>
         <ul>
          <li><a href="javascript:wOrg('6110')">課</a></li>
          <li><a href="javascript:wOrg('6111')">総務係</a></li>
          <li><a href="javascript:wOrg('6112')">管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('612')">測量課</a>
         <ul>
          <li><a href="javascript:wOrg('6120')">課</a></li>
          <li><a href="javascript:wOrg('6121')">調査係</a></li>
          <li><a href="javascript:wOrg('6122')">測量第一係</a></li>
          <li><a href="javascript:wOrg('6123')">測量第二係</a></li>
         </ul>
        </li>
       </ul>
      </li>
      <li>
       <a href="javascript:wOrg('62')">東北</a>
       <ul>
        <li><a href="javascript:wOrg('620')">部</a></li>
        <li>
         <a href="javascript:wOrg('621')">管理課</a>
         <ul>
          <li><a href="javascript:wOrg('6210')">課</a></li>
          <li><a href="javascript:wOrg('6211')">総務係</a></li>
          <li><a href="javascript:wOrg('6212')">管理係</a></li>
        </ul>
       </li>
       <li>
        <a href="javascript:wOrg('622')">測量課</a>
         <ul>
          <li><a href="javascript:wOrg('6220')">課</a></li>
          <li><a href="javascript:wOrg('6221')">調査係</a></li>
          <li><a href="javascript:wOrg('6222')">測量第一係</a></li>
          <li><a href="javascript:wOrg('6223')">測量第二係</a></li>
         </ul>
        </li>
       </ul>
      </li>
      <li>
       <a href="javascript:wOrg('63')">関東</a>
       <ul>
        <li><a href="javascript:wOrg('630')">部</a></li>
        <li>
         <a href="javascript:wOrg('631')">管理課</a>
         <ul>
          <li><a href="javascript:wOrg('6310')">課</a></li>
          <li><a href="javascript:wOrg('6311')">総務係</a></li>
          <li><a href="javascript:wOrg('6312')">管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('632')">測量課</a>
         <ul>
          <li><a href="javascript:wOrg('6320')">課</a></li>
          <li><a href="javascript:wOrg('6321')">調査係</a></li>
          <li><a href="javascript:wOrg('6322')">測量第一係</a></li>
          <li><a href="javascript:wOrg('6323')">測量第二係</a></li>
          <li><a href="javascript:wOrg('6324')">成果係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('633')">防災課</a>
         <ul>
          <li><a href="javascript:wOrg('6330')">課</a></li>
          <li><a href="javascript:wOrg('6331')">防災企画係</a></li>
          <li><a href="javascript:wOrg('6332')">防災情報係</a></li>
         </ul>
        </li>
       </ul>
      </li>
      <li>
       <a href="javascript:wOrg('64')">北陸</a>
       <ul>
        <li>
         <a href="javascript:wOrg('640')">部</a>
        </li>
        <li>
         <a href="javascript:wOrg('641')">管理課</a>
         <ul>
          <li><a href="javascript:wOrg('6410')">課</a></li>
          <li><a href="javascript:wOrg('6411')">総務係</a></li>
          <li><a href="javascript:wOrg('6412')">管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('642')">測量課</a>
         <ul>
          <li><a href="javascript:wOrg('6420')">課</a></li>
          <li><a href="javascript:wOrg('6421')">調査係</a></li>
          <li><a href="javascript:wOrg('6422')">測量第一係</a></li>
          <li><a href="javascript:wOrg('6423')">測量第二係</a></li>
         </ul>
        </li>
       </ul>
      </li>
      <li>
       <a href="javascript:wOrg('65')">中部</a>
       <ul>
        <li><a href="javascript:wOrg('650')">部</a></li>
        <li>
         <a href="javascript:wOrg('651')">管理課</a>
         <ul>
          <li><a href="javascript:wOrg('6510')">課</a></li>
          <li><a href="javascript:wOrg('6511')">総務係</a></li>
          <li><a href="javascript:wOrg('6512')">管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('652')">測量課</a>
         <ul>
          <li><a href="javascript:wOrg('6520')">課</a></li>
          <li><a href="javascript:wOrg('6521')">調査係</a></li>
          <li><a href="javascript:wOrg('6522')">測量第一係</a></li>
          <li><a href="javascript:wOrg('6523')">測量第二係</a></li>
         </ul>
        </li>
       </ul>
      </li>
      <li>
       <a href="javascript:wOrg('66')">近畿</a>
       <ul>
        <li><a href="javascript:wOrg('660')">部</a></li>
        <li>
         <a href="javascript:wOrg('661')">管理課</a>
         <ul>
          <li><a href="javascript:wOrg('6610')">課</a></li>
          <li><a href="javascript:wOrg('6611')">総務係</a></li>
          <li><a href="javascript:wOrg('6612')">管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('662')">測量課</a>
         <ul>
          <li><a href="javascript:wOrg('6620')">課</a></li>
          <li><a href="javascript:wOrg('6621')">調査係</a></li>
          <li><a href="javascript:wOrg('6622')">測量第一係</a></li>
          <li><a href="javascript:wOrg('6623')">測量第二係</a></li>
          <li><a href="javascript:wOrg('6624')">成果係</a></li>
         </ul>
        </li>
       </ul>
      </li>
      <li>
       <a href="javascript:wOrg('67')">中国</a>
       <ul>
        <li><a href="javascript:wOrg('670')">部</a></li>
        <li>
         <a href="javascript:wOrg('671')">管理課</a>
         <ul>
          <li><a href="javascript:wOrg('6710')">課</a></li>
          <li><a href="javascript:wOrg('6711')">総務係</a></li>
          <li><a href="javascript:wOrg('6712')">管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('672')">測量課</a>
         <ul>
          <li><a href="javascript:wOrg('6720')">課</a></li>
          <li><a href="javascript:wOrg('6721')">調査係</a></li>
          <li><a href="javascript:wOrg('6722')">測量第一係</a></li>
          <li><a href="javascript:wOrg('6723')">測量第二係</a></li>
         </ul>
        </li>
       </ul>
      </li>
      <li>
       <a href="javascript:wOrg('68')">四国</a>
       <ul>
        <li><a href="javascript:wOrg('680')">部</a></li>
        <li>
         <a href="javascript:wOrg('681')">管理課</a>
         <ul>
          <li><a href="javascript:wOrg('6810')">課</a></li>
          <li><a href="javascript:wOrg('6811')">総務係</a></li>
          <li><a href="javascript:wOrg('6812')">管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('682')">測量課</a>
         <ul>
          <li><a href="javascript:wOrg('6820')">課</a></li>
          <li><a href="javascript:wOrg('6821')">調査係</a></li>
          <li><a href="javascript:wOrg('6822')">測量第一係</a></li>
          <li><a href="javascript:wOrg('6823')">測量第二係</a></li>
         </ul>
        </li>
       </ul>
      </li>
      <li>
       <a href="javascript:wOrg('69')">九州</a>
       <ul>
        <li><a href="javascript:wOrg('690')">部</a></li>
        <li>
         <a href="javascript:wOrg('691')">管理課</a>
         <ul>
          <li><a href="javascript:wOrg('6910')">課</a></li>
          <li><a href="javascript:wOrg('6911')">総務係</a></li>
          <li><a href="javascript:wOrg('6912')">管理係</a></li>
         </ul>
        </li>
        <li>
         <a href="javascript:wOrg('692')">測量課</a>
         <ul>
          <li><a href="javascript:wOrg('6920')">課</a></li>
          <li><a href="javascript:wOrg('6921')">調査係</a></li>
          <li><a href="javascript:wOrg('6922')">測量第一係</a></li>
          <li><a href="javascript:wOrg('6923')">測量第二係</a></li>
          <li><a href="javascript:wOrg('6923')">測量第二係</a></li>
         </ul>
        </li>
       </ul>
      </li>
     </ul>
    </li>
    <li>
     <a class="_top" href="javascript:wGrp2('0')">▼職種別</a>
     <ul>
      <li><a href="javascript:wGrp2('1')">職員</a></li>
      <li><a href="javascript:wGrp2('2')">非常勤職員</a></li>
     </ul>
    </li>
   </ul>
   <br>
   <div class="_v20px"></div>
   <form name="f1" method="get">
    <ul class="_balloon">
     <li>
      <input type="text" id="text_search" name="keyword" value="#{$KEYWORD}" placeholder="キーワード"/><select name="and_or" onChange="submit()">#{sSelectAndOr}</select>
      <ul>
       <li>
        <span>
         <font class="_b1">複数のキーワードは 空白 で区切ってください。</font>
         <br>
         <font class="_b2">AND：[総務部 グループ] ⇒ [総務部 かつ グループ] を検索します。</font>
         <br>
         <font class="_b2">OR&nbsp;：[部長 センター長] ⇒ [部長 もしくは センター長] を検索します。</font>
         <br>
         <font class="_b2">NOR：[部長 センター長] ⇒ [部長 もしくは センター長] 以外 を検索します。</font>
         <br>
        </span>
       </li>
      </ul>
     </li>
    </ul>
    <input type="button" id="button_init" value="×" onClick="wReset()"/>
   </form>
  </td>
 </tr>
</table>
EOD
	return rtn
end

def
rtnStrToHtml(
	ln,      # 行
	keyword, # 検索ワード
	org,     # 所属ID
	grp1,    # 勤務先ID
	grp2     # 職員種ID
)
	# TSV対応
	ary = ln.split("\t")

	if ln =~ /#{keyword}/i && ary[4] =~ /#{org}/ && ary[9] =~ /#{grp1}/ && ary[10] =~ /#{grp2}/ 
		$SearchCnt += 1 # 検索件数

		return(
			" " +
			"<tr>" +
			"<td>#{ary[5]}</td>" + # 部
			"<td>#{ary[6]}</td>" + # 課
			"<td>#{ary[7]}</td>" + # 係
			"<td>#{ary[3]}</td>" + # 役職
			"<td><div class=\"_hurigana\">#{ary[2]}</div><div name=\"_output1\">#{ary[1]}</div></td>" + # よみ、氏名
			"<td name=\"_output2\"><a href=\"mailto:#{ary[0]}\">#{ary[0]}</a></td>" + # email
			"</tr>\n"
		)
	else
		return ""
	end
end

def
rtnHtml2PageSearchResult()
	$SearchCnt = 0 # 検索件数初期化
	allCnt = 0     # 全データ数

	aTmp = []

	$_KEYWORD.split("\t").each do
		|s|
		s.strip!
		case $_AND_OR
			when "AND"
				aTmp << "(?=.*#{s})"
			when "NOR"
				aTmp << "(?!.*#{s})"
			else
				aTmp << s
		end
	end

	keyword = ""

	case $_AND_OR
		when "AND", "NOR"
			keyword = "^#{aTmp.join}.*$"
		else
			keyword = aTmp.join("|")
	end

	result = ""

	File.read($IFN).split("\n").each do
		|ln|
		result << rtnStrToHtml(ln, keyword, $_ORG, $_GRP1, $_GRP2)
		allCnt += 1
	end

	return(
		"<div class=\"_v10px\"></div>\n" +
		"<font class=\"_a2\">【該当 #{$SearchCnt}件／#{allCnt}件中】</font>&nbsp;&nbsp;<font class=\"_a3\">[部／課]リンクから座席表を表示します.</font>\n" +
		"<table style=\"margin:0 0 0 4px;\">\n" +
		" " +
		"<tr>" +
		"<th>部</th>" +
		"<th>課</th>" +
		"<th>係</th>" +
		"<th>役職</th>" +
		"<th>氏名</th>" +
		"<th>email</th>" +
		"</tr>\n" +
		result +
		"</table>\n" +
		"<div class=\"_v20px\"></div>\n" +
		"<form style=\"margin:0 0 0 4px;\">\n" +
		" <textarea id=\"_textarea11\"><!-- JSで生成 --></textarea>\n" +
		" <div class=\"_v2px\"></div>\n" +
		" <input type=\"button\" value=\"メール作成\" onClick=\"eSendMail('_textarea11')\"/>\n" +
		" <input type=\"button\" value=\"コピー\" onClick=\"eCopy('_textarea11')\"/>\n" +
		"</form>\n"
	)
end

def
rtnHtml2PageMsg()
rtn = <<EOD
EOD
	return rtn
end

def
rtnHtml1Footer()
rtn = <<EOD
<br>
<a name="9">#9</a>
</body>
<script>
window.onload = function()
{
	with(document.getElementById("text_search"))
	{
		focus();
		var len = value.length;
		setSelectionRange(len, len);
	}
}
function wReset()
{
	window.open("?", "_self");
}
function wOrg(
	org
)
{
	window.open("?org=" + org, "_self");
}
function wGrp1(
	grp1
)
{
	window.open("?grp1=" + grp1, "_self");
}
function wGrp2(
	grp2
)
{
	window.open("?grp2=" + grp2, "_self");
}
function wOrder(
	order
)
{
	window.open("?order=" + order, "_self");
}
function eSendMail(
	textareaId
)
{
	location.href = "mailto:" + document.getElementById(textareaId).value;
}
function eCopy(
	textareaId
)
{
	document.getElementById(textareaId).select();
	document.execCommand("copy");
}
</script>
<div class="_v200px"></div>
</html>
EOD
	return rtn
end

#---------------------------------------------------------------------
# Main
#---------------------------------------------------------------------
# 入力ファイルが存在しないとき exit()
if ! File.exist?($IFN)
	puts(
		"Content-type:text/html;charset=UTF-8\n\n" +
		"Not exist a input file !"
	)
	exit()
end

$BgnTm = Time.now

# Header
print rtnHtml1Header()
print rtnHtml2PageHeader()
print rtnHtml2PageSearch()

# Result or Help
print (($KEYWORD || $ORG || $GRP1 || $GRP2) ? rtnHtml2PageSearchResult() : rtnHtml2PageMsg())

# Footer
print rtnHtml1Footer()

# 隠し情報
puts "<!-- #{$VERSION} -->"
puts "<!-- #{Time.now - $BgnTm}sec -->"
