# Updates

## 06/25/2021

First alpha release of the plugin, for proof of concept purposes. I would not consider the program to be in beta, as plenty of the functionality is incomplete and require further code work and refinement. That and other functionality is also worth exploring as well.

### Known bugs

- In KiCAD nightly, the `SaveBoard()` function closes KiCAD every time it is executed, However, the modified PCB is still generated and appears in the specified in the output directory
- The GUI is currently a blocking-type application, which will cause some functional issues when exiting a program. This is currently under investigation and major rework is in the works.

### Future Work

- Since there is a proof of concept for a Skidl keyboard PCB generator with switchable parts, I am considering researching a way to integrate Skidl into KiCAD-stable PCBs.
- There exists a function for getting a board's bounding box in KiCAD, which can be exploited to generate board edges for further use.
- Changing the unit step size, as currently the board defaults to `19.05 mm`. This will be useful for placing components other than key clusters.
