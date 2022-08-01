import logging
import os
import re
import shutil
import subprocess
import sys

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger("submodule-converter")
logger.setLevel(logging.DEBUG)


def main():
    start = "."
    for root, dirs, files in os.walk(start):
        if root != start and ".git" in dirs:
            config = os.path.join(root, ".git", "config")
            with open(config, "r") as f:
                content = f.read()
            matches = re.search("^\s*url = (.*)$", content, flags=re.MULTILINE)
            if not matches:
                logger.warning(f"Could not find remote url for {root}")
                continue
            print("-------------------------------------")
            logger.info(f"Converting {root} to submodule")
            url = matches.groups()[0]
            backup_dir = f"{root}-backup"
            shutil.move(root, backup_dir)
            logger.info(f"Created backup directory: {backup_dir}")
            try:
                subprocess.run(f"git rm --cached {root}", shell=True)
                subprocess.run(
                    f"git submodule add {url} {root} --force", shell=True, check=True
                )
            except subprocess.CalledProcessError:
                logger.exception(f"Could not add git submodule: {url}")
                logger.info("Restoring backup")
                shutil.move(backup_dir, root)
                print("")
                continue
            shutil.rmtree(backup_dir)
            logger.info("Removed backup directory")
            print("")


if __name__ == "__main__":
    main()
