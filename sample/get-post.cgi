#!mruby+cgi.exe
##/usr/bin/env mruby+cgi
#coding:utf-8

$TITLE = "Mruby-CGI"

#---------------------------------------------------------------------
# HTML template
#---------------------------------------------------------------------
def
HTML(
	body = nil,
	hQS = {}
)
return <<EOD
Content-type:text/html;charset=UTF-8

<!DOCTYPE html>
<html lang="ja">
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<meta http-equiv="Content-Script-Type" content="text/javascript">
<title>#{$TITLE}</title>
<style type="text/css">
@charset "utf-8";
</style>
</head>
<body>
<h2>Hello Mruby-CGI!!</h2>
<form name="f1" method="get">
 <input type="text" name="GET" value="#{hQS['GET']}" placeholder="GET"/>
 <input type="submit" value="Submit">
 <input type="reset" value="Reset" onClick="wReset()">
</form>
<form name="f2" method="post">
 <input type="text" name="POST" value="#{hQS['POST']}" placeholder="POST"/>
 <input type="submit" value="Submit">
 <input type="reset" value="Reset" onClick="wReset()">
</form>
<br>
#{body}
</body>
<script>
function wReset()
{
	window.open("?", "_self");
}
</script>
</html>
EOD
end

#---------------------------------------------------------------------
# iwm-iwama20200705
#---------------------------------------------------------------------
#-------------
# URI decode
#-------------
def
IwmRtnUriDecode(
	uri = nil
)
	return(
		uri ?
		uri.gsub("+", " ").gsub(/%([a-fA-F0-9][a-fA-F0-9])/){ $1.hex.chr } :
		""
	)
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
			qs = $stdin.read(255) # バイト数指定
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

#--------------------------------------------------------------------
# Main
#--------------------------------------------------------------------
body = ""

hQS = IwmRtnHashQueryString()

hQS.each do
	|k, v|
	body << "['#{k}'] = '#{v}'<br>"
end

print HTML(body, hQS)
