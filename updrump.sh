add_templates.py
rm -rf rumpkit
git clone https://github.com/Infinitybotlist/rumpkit
cp -rf rumpkit/* $1
rm -rf $1/README.md
