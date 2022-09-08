import os, shutil, uuid, json

def run_fast_scandir(dir):    # dir: str, ext: list
    subfolders, files = [], []

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            files.append(f.path)


    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files

def mkdir(folder, exists_ok = True):
    try:
        os.system(f"rm -rvf {folder}")
    except Exception as exc:
        print(exc)

    os.mkdir(folder)

mkdir("out", exists_ok=True)

subfolders, files = run_fast_scandir("..")

files_b = files

with open("template/index.html") as f:
    r = f.read()

    if os.path.exists("static/ext.css"):
        r = r.replace("$extstyle", """<link rel="stylesheet" href="/static/ext.css?n=$ver" />""")
    else:
        r = r.replace("$extstyle", "")

    r = r.replace("$ver", str(uuid.uuid4()))


tmpid = uuid.uuid4()

with open(f"{tmpid}", "w") as f:
    f.write(r)

cwd = os.getcwd().split("/")[-1]
print("Rumpkit\nCurrent folder:", cwd)

print("BUILD: Adding routes")

for subfolder in subfolders:
    if ".git" in subfolder or "_" in subfolder or subfolder.startswith(("./template", "./bin")):
        continue
    
    if f"{subfolder}/+route" in subfolders:
        print("Adding", subfolder.replace(f"../", "", 1).replace(cwd, "", 1) or "/")
        parsed_subfolder = subfolder.replace(f"../", "", 1).replace(cwd, "", 1) or "/"
        mkdir(f"out{parsed_subfolder}", exists_ok=True)
        mkdir(f"out{parsed_subfolder}/+route", exists_ok=True)
        mkdir(f"out{parsed_subfolder}/+data", exists_ok=True)
        shutil.copy2(f"{tmpid}", f"out{parsed_subfolder}/index.html")
        
        cp_sf = "" if parsed_subfolder == "/" else parsed_subfolder.replace("/", "", 1) + "/"

        os.system(f"cp -rvf {cp_sf}+data out{parsed_subfolder}")
        

        # Filelist generation support (for +data)
        if f"{subfolder}/+route/@filelist" in files:
            print("Adding", subfolder.replace(f"../", "", 1).replace(cwd, "", 1) or "/", "filelists (due to @filelist)")
            _, _files = run_fast_scandir(f"{subfolder}/+data")

            files = []
            for f in _files:
                fc = f.replace(f"{subfolder}/+data", "") or "/"
                if fc == "/filelist.json":
                    continue
                files.append(fc)

            with open(f"out{parsed_subfolder}/+data/filelist.json", "w") as f:
                json.dump({"files": files}, f)

try:
    os.remove(f"{tmpid}")
except OSError:
    pass

print("BUILD: Copying static files")
os.system("cp -rf static out")

print("BUILD: Attempting to minify .js files")

# https://stackoverflow.com/questions/2556108/rreplace-how-to-replace-the-last-occurrence-of-an-expression-in-a-string
def rreplace(s, old, new, count):
    return (s[::-1].replace(old[::-1], new[::-1], count))[::-1]

for file in files:
    _file = file.replace(f"../", "", 1).replace(cwd, "", 1).replace("/", "", 1)
    if _file.endswith(".js") and not _file.endswith(".min.js"):
        print("Minifying+optimizing", _file)
        os.system(f"google-closure-compiler --js {_file} --js_output_file out/{rreplace(_file, '.js', '.min.js', 1)}")

print("\n\nThe 'out' folder can be served")