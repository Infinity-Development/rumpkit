mkdir -p $1
rm -rf rumpkit
git clone https://github.com/Infinity-Development/rumpkit
cp -rf rumpkit/* $1
rm -rf $1/{README.md,mkrump.sh}
rm -rf rumpkit

npm i -g google-closure-compiler
