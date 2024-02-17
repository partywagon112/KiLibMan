# KiLibMan - Kicad Library Manager

A self hostable Python Dash server that assists you in managing your library. 

The server acts as a front end to a self hosted git repository, and uses submodules to form the library dependencies. It centralises remote symbol and footprint libraries into one single repository for you to clone and manage. It generates the sym_lib_table and fp_lib_tables for you to integrate on your system, and allows you to recieve symbol updates. 

I'm mostly doing this as a learning thing; trying to figure out the memory/computing balance... It's a challenge in this one.

## Future
- Hoping to get a since SnapEDA interface to add symbols and footprints into your library.
- Manage templates and 3d models remotely, and generate previews.
- Integrate a HTTP library. I designed this to use with Inventree, and the plugin for hosting an kicad_httplib is currently there - but I believe it would make more sense being hosted alongside the library... or this be integrated into Inventree?? Many choices!