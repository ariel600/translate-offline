import os
import sys

import argostranslate.package as p

langs = sys.argv[1:]
p.update_package_index()
installed = {(x.from_code, x.to_code) for x in p.get_installed_packages()}
for pkg in p.get_available_packages():
    wanted = not langs or (pkg.from_code in langs and pkg.to_code in langs)
    if wanted and (pkg.from_code, pkg.to_code) not in installed:
        print("Installing", pkg, flush=True)
        archive = pkg.download()
        p.install_from_path(archive)
        os.remove(archive)
print("Installed:", len(p.get_installed_packages()))
