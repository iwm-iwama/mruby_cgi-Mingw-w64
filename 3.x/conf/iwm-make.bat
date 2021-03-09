@echo off
cls
call rake clean
ruby minirake
pushd "build\host\bin"
strip *.exe
ren mruby.exe mruby+cgi.exe
popd
pause
exit
