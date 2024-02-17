import kiutils.libraries
from abc import ABCMeta, abstractmethod, abstractclassmethod, abstractproperty
import os
from tqdm import tqdm
import kiutils_extension
import re
import logging
import threading
import shutil

class KicadRepository(metaclass=ABCMeta):
    def __init__(self, path, base_env):
        """
        Metaclass describing the anatomy of a symbol of footprint repository.
        """
        self.path: str = path
        self.base_env: str = base_env

        self.lib_table: kiutils.libraries.LibTable = self.load_lib_table()
        self.remove_bad_libraries()
        # self.libraries: dict = self.load_libraries_from_table()
        # self.libraries: dict = self.load_libraries_from_table()

        if not os.path.exists(self.path):
            os.mkdir(self.path)
            self.to_file()
    
    def remove_bad_libraries(self):
        bad_libraries = []
        for lib in self.lib_table.libs:
            if not os.path.exists(self.resolve_uri(lib.uri)):
                bad_libraries.append(lib)

        [self.lib_table.libs.remove(lib) for lib in bad_libraries]
    
    # def load_empty_library_dictionary(self):
    #     for lib in self.lib_table.libs:
    #         self.libraries[lib.name] = None

    @abstractproperty
    def lib_table_name(self):
        pass

    @abstractproperty
    def library_extension(self):
        pass

    @abstractproperty
    def library_type(self) -> kiutils_extension.KicadUtilsLib:
        pass

    def __read_library_thread_cb(self, lib, library_path):
        logging.debug(f"Creating new thread for {lib.name}")
        print(f"Started reading {lib.name}")

        self.libraries[lib.name] = self.library_type.from_file(library_path)
        print(f"Finished importing {lib.name}")

    def load_libraries_from_table(self):
        self.libraries = {}
        bad_libraries = []
        threads:list[threading.Thread] = []

        for lib in tqdm(self.lib_table.libs, desc=f"Loading libraries from {self.path}"):
            library_path = os.path.normpath(self.resolve_uri(lib.uri))

            if re.match(r"\${.*}", library_path):
                raise FileNotFoundError(f"Failed to resolve path {library_path}")
            if not os.path.exists(library_path):
                bad_libraries.append(lib)
                continue

            thread = threading.Thread(target=self.__read_library_thread_cb, args=(lib, library_path), daemon=True)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

            # Note this threading method replaces the other method.
            # self.libraries[lib.name] = self.library_type.from_file(library_path)

        # Can't remove dynamically because of indexing issues...
        [self.lib_table.libs.remove(lib) for lib in bad_libraries]

        return self.libraries

    def lib_table_from_path(self) -> kiutils.libraries.LibTable:
        self.lib_table = kiutils.libraries.LibTable.create_new(self.lib_table_name.replace("-", "_"))

        if not os.path.exists(self.path):
            os.mkdir(self.path)

        for path in os.listdir(self.path):
            if path.endswith(self.library_extension):
                lib_name = path.split("/")[-1]
                self.lib_table.libs.append(kiutils.libraries.Library(lib_name.removesuffix(self.library_extension), uri=f"{self.base_env}/{lib_name}"))

        return self.lib_table

        # self.libraries = {
        #     library_name: self.library_type.from_file(os.path.join(self.path, library_name)) 
        #     for library_name 
        #     in tqdm(
        #         [path for path in os.listdir(self.path) if path.endswith(self.library_extension)], 
        #         desc=f"Loading libraries from: {self.path}", leave=True, position=0)
        # }

    def to_dict(self):
        if self.lib_table_name == "sym-lib-table":
            return {library_name: [symbol.entryName for symbol in library.symbols] for library_name, library in self.libraries.items()}
        if self.lib_table_name == "fp-lib-table":
            return {library_name: [footprint.entryName for footprint in library.footprints] for library_name, library in self.libraries.items()}
        raise TypeError("Repository has been incorrectly defined.")

    # def to_file(self, path=None):
    #     if path == None:
    #         if self.path == None:
    #             raise FileNotFoundError("No path specified!")
    #         path = self.path
    #     if not os.path.exists(path):
    #         os.mkdir(path)

    #     # save the lib_table
    #     self.lib_table.to_file(os.path.join(path, self.lib_table_name))

    #     # save libraries
    #     for lib_table_lib in tqdm(self.lib_table.libs, desc="Saving libraies to file"):
    #         if lib_table_lib.name in self.libraries.keys():
    #             # print(lib_table_lib.uri.replace(self.base_env, path))
    #             self.libraries[lib_table_lib.name].to_file(lib_table_lib.uri.replace(self.base_env, path))

    def load_lib_table(self) -> kiutils.libraries.LibTable:
        lib_table_path = os.path.join(self.path, self.lib_table_name)

        if os.path.exists(lib_table_path):
            return kiutils.libraries.LibTable.from_file(lib_table_path)

        return self.lib_table_from_path()

    def load_new_lib_table_base_env(self, new_base_env) -> kiutils.libraries.LibTable:
        for index, lib in enumerate(self.lib_table.libs):
            self.lib_table.libs[index].uri = lib.uri.replace(self.base_env, new_base_env)
        self.base_env = new_base_env
        return self.lib_table

    def resolve_uri(self, uri: str):
        # print(self.base_env, uri)
        result = uri.replace(self.base_env, self.path)
        return result

    @abstractmethod
    def merge_repository(self, remote_repository):
        pass

    def merge_library(self, destination_library: kiutils_extension.KicadUtilsLib, library: kiutils_extension.KicadUtilsLib, override_existing: bool = True):
        """
        Merges in symbol library to destination library.

        Allows for an override.
        """
        to_entries = {part.entryName: index for index, part in enumerate(destination_library.parts)}

        for part in tqdm(library.parts, desc=f"Merging library {destination_library.filePath}"):

            print(f"Checking part {part.entryName}")

            if part.entryName not in to_entries.keys():
                print(f"Adding from remote part {part.entryName}")
                destination_library.parts.append(part)

            else:
                print(f"{part.entryName} already exists")
                # If we have an entry and found a symbol, then add it in.
                if override_existing == True:
                    print(f"Overriding {part.entryName} at index {to_entries[part.entryName]}")
                    destination_library.parts[to_entries[part.entryName]]

        return destination_library

class KicadSymbolRepository(KicadRepository):      
    @property  
    def library_type(self):
        return kiutils_extension.SymbolLib

    @property
    def lib_table_name(self):
        return "sym-lib-table"
    
    @property
    def library_extension(self):
        return ".kicad_sym"
    
    def merge_repository(self, remote_repository: KicadRepository, override_existing: bool = False):
        remote_repository.lib_table = remote_repository.load_new_lib_table_base_env(self.base_env)
        self_lib_names = {lib.name: lib.uri for lib in self.lib_table.libs}

        for lib in tqdm(remote_repository.lib_table.libs, desc="Merging remote library"):
            if lib.name not in self_lib_names.keys():
                logging.info(f"Adding library {lib.name}")
                self.lib_table.libs.append(lib)

                print("Copying library.")
                shutil.copyfile(remote_repository.resolve_uri(lib.uri), self.resolve_uri(lib.uri))

                # self.libraries[lib.name] = repository_to_merge.libraries[lib.name]

            else:
                logging.info(f"Merging library {lib.name}")

                source_library = self.library_type.from_file(remote_repository.resolve_uri(lib.uri))
                destination_library = self.library_type.from_file(self.resolve_uri(self_lib_names[lib.name]))

                source_library: kiutils_extension.KicadUtilsLib = self.merge_library(destination_library, source_library, override_existing=override_existing)
                source_library.to_file(self.resolve_uri(self_lib_names[lib.name]))
        
        # remove the bad libraries...
        []

class KicadFootprintRepository(KicadRepository):        
    @property
    def library_type(self):
        return kiutils_extension.FootprintLib

    @property
    def lib_table_name(self):
        return "fp-lib-table"
    
    @property
    def library_extension(self):
        return ".pretty"

    def merge_repository(self, remote_repository: KicadRepository, override_existing:bool = False):
        remote_repository.lib_table = remote_repository.load_new_lib_table_base_env(self.base_env)
        self_lib_names = {lib.name: lib.uri for lib in self.lib_table.libs}

        for lib in tqdm(remote_repository.lib_table.libs, desc="Adding in footprints"):
            if lib.name == "Audio_Module":
                print("HERE")
            print(f"GOING TO {self.resolve_uri(lib.uri)}")
            shutil.copytree(remote_repository.resolve_uri(lib.uri), self.resolve_uri(lib.uri), dirs_exist_ok=override_existing)
