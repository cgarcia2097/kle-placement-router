# Dependencies

When running inside KiCAD as a plugin, the program should be self-contained in terms of GUI and backend dependencies. But for reference, the project depends on:

- Python 3.8
- wxPython (the non-Phoenix version)
- PCBNew

## Installing the plugin

- Configure the Makefile to point to the KiCAD plugins directory. This can be done by editing these lines

    *KiCAD nightly* : `KICAD_NIGHTLY_PLUGIN_DIR=~/.local/share/kicad/5.99/scripting/plugins/`

    *KiCAD stable* : `KICAD_STABLE_PLUGIN_DIR=~/.kicad_plugins/`

- In a terminal window, run `make push` to push the KLEPR folder into the plugins directory to `nightly` and `stable`
- In PCBNew (either version), open `Tools`->`Scripting Terminal`
- In the terminal window, click `Options`->`Startup`->`Edit Startup Script`
- Add the following lines inside the startup script:

    ```python
    # Add this line to import the plugin into the KiCAD shell
    from klepr import app

    # If you want to mess with the individual functions
    # Uncomment these lines below
    # from klepr.kleprtools import pcb
    # from klepr.kleprtools import key
    ```

- Reopen the KiCAD shell, and run this command in the terminal:

    `app.main()`

- On success, the KLEPR window should open and be ready for use

## Support

The program is currently tested to run on KiCAD stable and KiCAD nightly, on Linux Mint 20 Cinnamon. No testing has been done on Windows at the moment.
