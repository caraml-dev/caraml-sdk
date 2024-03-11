import glob
import os

DUMMY_PACKAGES = {"caraml/models/": "merlin/", "caraml/routers/": "turing/"}
IGNORE_PATH = ["caraml/models/client", "caraml/models/docs", "caraml/routers/client"]


def _create_proxy(root, source, target):
    module = source.replace(root, '').replace('.py', '').replace('/', '.').replace('.__init__', '')
    
    # TODO: [Future] Can add a warning to provide help text/link to move to new caraml clients instead of the old ones
    import_line = f"from {module} import *" 
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, 'w') as target_file:
        target_file.write(import_line)

def main(root_dir: str):
    if not root_dir[-1] == "/":
        root_dir += "/"
    for module, target in DUMMY_PACKAGES.items():
        for filename in glob.iglob(root_dir + module + "**/*.py", recursive=True):
            if any(ip in filename for ip in IGNORE_PATH):
                continue
            target_path = filename.replace(module, target)
            print(f"Creating dummy for {filename}, at {target_path}")
            _create_proxy(root_dir, filename, target_path)


if __name__ == "__main__":
    import fire

    fire.Fire(main)
