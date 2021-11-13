@echo off
cls
call rake clean
call rake MRUBY_CONFIG="./build_config/mruby+cgi.rb"
pushd "./build/host/bin"
strip *.exe
ren mruby.exe mruby+cgi.exe
popd
pause
exit
