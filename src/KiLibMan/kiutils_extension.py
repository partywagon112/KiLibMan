from dataclasses import dataclass
import kiutils.libraries
import kiutils.footprint
import kiutils.symbol
from abc import ABCMeta, abstractmethod, abstractclassmethod, abstractproperty
import os
import subprocess

class KicadUtilsLib(metaclass=ABCMeta):
    @abstractclassmethod
    def from_file(cls, filepath):
        pass

    @abstractmethod
    def to_svgs(self):
        pass

    @abstractproperty
    def parts(self):
        return

@dataclass
class FootprintLib():
    """
    Hacked up version of the SymbolLib class to suit a footprint library.
    """
    filePath: str
    footprints: list[kiutils.footprint.Footprint]

    @classmethod
    def from_file(cls, filepath):
        footprints = [os.path.join(filepath, filename) for filename in os.listdir(filepath) if filename.endswith(".kicad_mod")]
        return cls(
            filePath=filepath, 
            footprints=[kiutils.footprint.Footprint.from_file(footprint_filepath) for footprint_filepath in footprints]
        )
    
    @property
    def parts(self):
        return self.footprints

    def to_file(self, filepath = None, encoding: str = None):
        if filepath is None:
            if self.filePath is None:
                raise Exception("File path not set")
            filepath = self.filePath
        
        if not os.path.exists(filepath):
            os.mkdir(filepath)

        for footprint in self.footprints:
            footprint.to_file(os.path.join(filepath, footprint.entryName), encoding)

    @classmethod
    def from_sexpr(cls, sexpreses: list):
        cls(filePath=None, footprints=[kiutils.footprint.Footprint.from_sexpr(sexpres) for sexpres in sexpreses])
    
    def to_sexpr(self, indent: int = 0, newline: bool = True) -> list:
        # NOTE return list of sexpres
        return [footprint.to_sexpr(indent, newline) for footprint in self.footprints]
    
    def to_svgs(self, filepath: str = None, opts: list = None):
        # Use this to export to SVG of the entire .pretty. If filepath is not defined, the will export into the 
        """
        Usage: svg [-h] [--output VAR] [--layers VAR] [--theme VAR] [--footprint VAR] [--black-and-white] input

        Positional arguments:
        input                 Input file

        Optional arguments:
        -h, --help            shows help message and exits
        -o, --output          Output file name [default: ""]
        -l, --layers          Comma separated list of untranslated layer names to include such as F.Cu,B.Cu [default: ""]
        -t, --theme           Color theme to use (will default to pcbnew settings) [default: ""]
        --fp, --footprint     Specific symbol to export within the library [default: ""]
        --black-and-white     Black and white only
        """
        if filepath is None:
            if self.filePath is None:
                raise Exception("File path not set")
            filepath = self.filePath

        subprocess.run(f"\"C:\\Program Files\KiCad\\7.0\\bin\kicad-cmd.bat\" && kicad-cli fp export svg -o \"{filepath}\" \"{self.filePath}\"", shell=True)

@dataclass
class SymbolLib(kiutils.symbol.SymbolLib):
    """
    Extension to support svg export method
    """
    @property
    def parts(self):
        return self.symbols

    def to_svgs(self, filepath: str = None, opts: list = None):
        # Use this to export to SVG of the entire .pretty. If filepath is not defined, the will export into the 
        """
        Usage: svg [-h] [--output VAR] [--layers VAR] [--theme VAR] [--footprint VAR] [--black-and-white] input

        Positional arguments:
        input                 Input file

        Optional arguments:
        -h, --help            shows help message and exits
        -o, --output          Output file name [default: ""]
        -l, --layers          Comma separated list of untranslated layer names to include such as F.Cu,B.Cu [default: ""]
        -t, --theme           Color theme to use (will default to pcbnew settings) [default: ""]
        --fp, --footprint     Specific symbol to export within the library [default: ""]
        --black-and-white     Black and white only
        """
        if filepath is None:
            if self.filePath is None:
                raise Exception("File path not set")
            filepath = self.filePath

        subprocess.run(f"\"C:\\Program Files\KiCad\\7.0\\bin\kicad-cmd.bat\" && kicad-cli sym export svg -o \"{self.filepath}\" \"{self.filePath}\"", shell=True)
