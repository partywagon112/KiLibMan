@echo off

pushd .\testing
mkdir Repository
pushd Repository
git init

mkdir remotes
pushd remotes

git submodule add "https://gitlab.com/kicad/libraries/kicad-symbols.git" symbols\kicad-symbols
git submodule add "https://gitlab.com/kicad/libraries/kicad-footprints.git" footprints\kicad-footprints
git submodule add "https://gitlab.com/kicad/libraries/kicad-packages3d.git" packages3d\kicad-packages3d
git submodule add "https://gitlab.com/kicad/libraries/kicad-templates.git" templates\kicad-templates

pushd ..\
mkdir symbols
mkdir footprints
mkdir packages3d
mkdir templates

:: Add this into the pythom modules
