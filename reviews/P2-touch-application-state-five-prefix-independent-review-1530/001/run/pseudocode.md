# Startup with original state-five preparation

Original 6A80 and its reset helper 685C execute during the first calibration state-five transition. The synthetic status word selects the reset wait-helper branch, so 6608(315,0,descriptor) remains explicitly controlled. Original ordered reset and three-row preparation writes execute. All inherited startup state checks, exact remaining call order and arrival at 3D50 pass.

Remaining calibration controls include 7288 acquisition and 5FA4 budget 1. Other activation/storage/later application boundaries remain controlled. Initialization data is authenticated; MMIO and external clock tables remain synthetic. Physical behavior and whole-firmware coverage remain unresolved. No canonical admission or C implementation.
