# Application prefix with original descriptor initializer

Actual 4C7C and its local 4C72 adapter now execute in the secondary interrupt initializer. The adapter is eight instruction bytes at4C72..4C7A: save R4/LR, call4C44 with unchanged incoming registers, restore and return rawresult; adjacent zero halfword remains excluded. Two deeper calls6AC0 and4C44 return zero through explicit controls without memory effects. The original initializer performs its descriptor/context/row writes from authenticated initialized data and proceeds to registration.

All prior clock, peripheral, interrupt, descriptor, settings, object and buffer assertions remain and stop3D50 is reached. Four storage calls,6AC0,4C44,4AF4 and two later application calls remain controlled. External clocktables are synthetic. Physical hardware, deeper setup and application loop completion remain unresolved. No canonical admission or C implementation.
