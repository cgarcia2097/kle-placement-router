# Configure the following directories to the appropriate KiCAD plugins directory
# The defaults are the base installation directories specified by the Debian package

KICAD_NIGHTLY_PLUGIN_DIR=~/.local/share/kicad/5.99/scripting/plugins/
KICAD_STABLE_PLUGIN_DIR=~/.kicad_plugins/
SRC_DIR=klepr/

# Removes the plugin from the nightly plugin directory

clean_nightly:
	rm -rfv $(KICAD_NIGHTLY_PLUGIN_DIR)$(SRC_DIR)

# Removes the plugin from the stable plugin directory

clean_stable:
	rm -rfv $(KICAD_STABLE_PLUGIN_DIR)$(SRC_DIR)

# Installs the plugin to the stable plugin directory

push_to_stable:
	cp -rv ./$(SRC_DIR) $(KICAD_STABLE_PLUGIN_DIR)

# Installs the plugin to the nightly plugin directory

push_to_nightly:
	cp -rv ./$(SRC_DIR) $(KICAD_NIGHTLY_PLUGIN_DIR)

# Run KiCAD-nightly with path name to a PCB

run_nightly:
	pcbnew-nightly $$PATH_TO_PCB

# Run KiCAD-stable with path name to the PCB

run_stable:
	pcbnew $$PATH_TO_PCB

# Remove the plugins from both stable and nightly

clean:
	make clean_nightly
	make clean_stable

# Install the plugins from both stable and nightly

push:
	make push_to_nightly
	make push_to_stable

# Clean reinstall of plugin to both stable and nightly

clean_push:
	make clean
	make push

# Kill any hanging processes just in case

kill_app:
	pkill pcbnew 
	pkill pcbnew-nightly
