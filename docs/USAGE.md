# Usage

These are the required for the plugin to work

- An unfinished PCB with all components on the board
  - All component references are in the format `"PREFIX_NUMBER"`, where `PREFIX` is the reference designator for the keyswitch and `NUMBER` being the cluster designator for the component (For example, "K_1" is a component with perfix "K_" belonging to cluster 1 of the layout. The underscore is important for parsing purposes; make sure that there's only one.
- A KLE layout file that matches the number of keys on your board
- An output directory in which the modified PCB is made

## Running the plugin

- Open the KiCAD scripting terminal and type `app.main()` into the terminal
- In KLEPR window click on `Browse` and select the KLE layout file from the file dialog
- Once the file is selected, add and and edit references to be placed based on prefix. This can be done by clicking `New`, selecting the new reference and clicking `Edit`.
- In the editing window, edit the settings as needed. As for the reference, make sure that your references contain an underscore between the prefix and the number.
- After adding all references, specify the output directory
- Click `Generate Layout`
- Check the output directory for `mod_.kicad_pcb`, which will be the name of the modified PCB (it doesn't change the existing PCB file, it saves changes to a new copy)

## Youtube Demostration

[![IMAGE ALT TEXT](http://img.youtube.com/vi/1WLOXQabQX0/0.jpg)](http://www.youtube.com/watch?v=1WLOXQabQX0 "KLE Placement Router Demo")
