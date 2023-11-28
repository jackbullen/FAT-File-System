make

./diskrm test.img mkfile.cc
./diskrm test.img foo.txt
./diskrm test.img disk.img.gz

cp test.img p3.img
rm test.img

python3 ./make_submission.py

make clean