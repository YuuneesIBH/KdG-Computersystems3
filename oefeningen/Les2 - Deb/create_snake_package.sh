#!/bin/bash

package="snake"
version="1"
mkdir -p "${package}/${package}-${version}"
cd "${package}/${package}-${version}"
cat > ${package} <<EOF
#!/bin/sh
# (C) 2011 Uname Zenity, GPL3+
zenity --warning --text="\`exec uname -a\`"
EOF
chmod 755 $package
cd ..
tar -cvzf ${package}-${version}.tar.gz ${package}-${version}