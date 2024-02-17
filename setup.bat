@echo off

set mypath=%cd%
call "C:\Program Files\KiCad\7.0\bin\kicad-cmd.bat"
cd %mypath%
call pip install -r requirements.txt

@REM @echo off

@REM mkdir Repository
@REM pushd Repository
@REM git init

@REM mkdir remotes
@REM pushd remotes
@REM git submodule add "https://gitlab.com/kicad/libraries/kicad-symbols.git"
@REM git submodule add "https://gitlab.com/kicad/libraries/kicad-footprints.git"
@REM git submodule add "https://gitlab.com/kicad/libraries/kicad-packages3d.git"
@REM git submodule add "https://gitlab.com/kicad/libraries/kicad-templates.git"

@REM pushd ..\
@REM mkdir symbols
@REM mkdir footprints
@REM mkdir packages3d
@REM mkdir templates
