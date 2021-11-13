#!/bin/bash
clear
rake clean
rake MRUBY_CONFIG="./build_config/mruby+cgi.rb"
pushd "./build/host/bin"
strip *
mv mruby mruby+cgi
popd
exit
