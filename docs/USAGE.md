# Usage

These are the required for the plugin to work

- An unfinished PCB with all components on the board
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