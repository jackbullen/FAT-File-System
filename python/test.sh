make
./diskinfo ../test.img > output/diskinfo.txt
./disklist ../test.img / > output/disklist.txt
./diskget ../test.img /foo.txt output/foo.txt
./diskget ../test.img /foo.txt output/disk.img.gz
./diskget ../test.img /disk.img.gz output/disk.img.gz
./diskget ../test.img /mkfile.cc output/mkfile.cc
make clean