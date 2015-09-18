from distutils.core import setup
import os
if os.name == "nt":
    import py2exe
DATA=[("", ["poewatcher/config.ini", "LICENSE", "README.md"]),
      ("extras/", ["extras/error.wav", "extras/warning.wav"])]
setup(
    name = 'poewatcher',
    packages = ['poewatcher'],
    scripts=['main.py', 'csv_sender.py'],
    version = '0.1b',
    description = 'PoE log watcher',
    author = 'Guillaume Dupuy',
    author_email = 'glorf@glorf.fr',
    url = 'https://github.com/Gloorf/watch_poe',
    license = 'AGPL v3+',
    keywords = ['poe'],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)"
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
    ],
    #py2exe stuff
    console =["main.py"],
    data_files = DATA,
    options={
            "py2exe": {
                        "packages" : ["poewatcher", "pyglet"],
                        "bundle_files":2,
                        "skip_archive": True
                      }
            }
)
