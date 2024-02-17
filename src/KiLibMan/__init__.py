import os
from appdata import AppDataPaths
import kiutils.symbol
import kiutils.footprint
import kiutils.libraries
import kiutils_extension
from kicad_repositories import KicadFootprintRepository, KicadSymbolRepository
import threading
from tqdm import tqdm
from abc import ABCMeta, abstractmethod, abstractclassmethod

from sys import getsizeof

from kiutils_extension import SymbolLib, FootprintLib
import yaml

APP_PATH = AppDataPaths('kicads-clown')
APP_PATH.setup()
LIBRARIES_PATH = os.path.join(APP_PATH.app_data_path, "Libraries")

class Remote():
    def __init__(self, uri="", name="", base_env="", envs=[]):
        self.url: str = str(uri)
        self.name: str = str(name)
        self.base_env: str = str(base_env)
        self.envs: list[dict] = envs

class Remotes():
    def __init__(self, symbols=[], footprints=[], packages3d=[], templates=[]):
        self.symbols: list[Remote] = [Remote(**symbol) for symbol in symbols]
        self.footprints: list[Remote] = [Remote(**footprint) for footprint in footprints]
        self.packages3d: list[Remote] = [Remote(**package3d) for package3d in packages3d]
        self.templates: list[Remote] = [Remote(**template) for template in templates]

class LibraryRepo():
    def __init__(self, repository_name, path, remotes, dump, **kwargs):
        self.path = str(path)
        self.base_env = f"${{{repository_name}}}"
        self.dump = dump

        self.remotes: Remotes = Remotes(**remotes)

        self.symbols = KicadSymbolRepository(path=os.path.join(self.path, "symbols"), base_env=f"{self.base_env}/symbols")
        self.footprints = KicadFootprintRepository(path=os.path.join(self.path, "footprints"), base_env=f"{self.base_env}/footprints")
        self.templates: dict = {}
        self.packages3d: dict = {}

    def update_symbols(self, reload: bool = False, override_existing: bool = True):
        if reload:
            self.symbols.load_lib_table()

        for remote in self.remotes.symbols:
            remote_symbols_path = os.path.join(self.path, "remotes", "symbols", remote.name)
            remote_repository = KicadSymbolRepository(remote_symbols_path, remote.base_env)
            self.symbols.merge_repository(remote_repository, override_existing)

    def update_footprints(self, reload: bool = True, override_existing: bool = True):
        if reload:
            self.footprints.load_lib_table()

        for remote in self.remotes.footprints:
            remote_path = os.path.join(self.path, "remotes", "footprints", remote.name)
            remote_repository = KicadFootprintRepository(remote_path, remote.base_env)
            self.footprints.merge_repository(remote_repository, override_existing)

    @classmethod
    def from_manifest(cls, filepath):
        with open(filepath, 'r') as file:
            manifest = yaml.safe_load(file)
            return cls(**manifest)

# remotes = Remotes.from_manifiest("manifest.yaml")
librepo = LibraryRepo.from_manifest("manifest.yaml")

# getsizeof(librepo)

librepo.update_symbols()
librepo.update_footprints()
# librepo.symbols.to_svgs(os.path.join(librepo.dump, "svgs"))

# print(librepo)
# librepo.update_symbol_library()


# repository = KicadSymbolRepository(os.path.join("testing", "Repository", "remotes", "symbols", "kicad-symbols"), "${KICAD7_SYMBOL_DIR}")
# print(repository.to_dict())

# repository = KicadFootprintRepository(os.path.join("testing", "Repository", "remotes", "footprints", "kicad-footprints"), "${KICAD7_FOOTPRINT_DIR}")
# print(repository.to_dict())

# repository.merge_library("Battery", repository.libraries["Capacitor_SMD"])
# repository.to_file("testing\\dump")