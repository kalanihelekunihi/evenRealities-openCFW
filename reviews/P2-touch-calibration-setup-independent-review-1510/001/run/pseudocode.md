# Calibration setup at 6928

The74-byte body [6928,6972) is followed by alignment and three literals. Resolve peripheral base through descriptor word0, configuration word8, then word0. Set control bit31. Write literal values to offsets120 and100, reading each back. Call9178(peripheral,6,inputScratchPointer). OR6 into the word at literal offset3034, reread and OR1, then write1 at3800. Return the helper status unchanged and restore frame.

Nine original-instruction fixtures check all six ordered MMIO writes, helper arguments, returned status, unchanged scratch under the explicit no-write helper control, and frame. 9178 effects andphysicalperipheral behavior remain unresolved; MMIO is synthetic. No canonical admission or C implementation.
