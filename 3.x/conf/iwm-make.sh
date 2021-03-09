#!/bin/bash
clear
rake clean
ruby minirake
pushd "build/host/bin"
strip *
mv mruby mruby+cgi
popd
exit
