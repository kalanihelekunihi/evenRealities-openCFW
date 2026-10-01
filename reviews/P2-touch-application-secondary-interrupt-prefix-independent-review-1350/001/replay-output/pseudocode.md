# Application prefix with secondary interrupt initialization

Actual 38E0 now executes its copied descriptor, interrupt priority and vector registration chain. Two deeper calls 4C7C and 4AF4 are controlled with zero returns and no memory effects. The original code installs callback 3949 at vector slot 24 (20000460), clears pending bit 8, and writes enable bit 8 after the earlier bit 7 command. Exact vector and ordered enable-register writes are asserted.

Four deeper storage calls, two deeper secondary initialization calls and two later application dependencies remain controlled. All earlier original clock, peripheral, buffer, descriptor, settings, object and SysTick checks remain; stop 3D50 is reached. External clock tables are synthetic. Physical interrupt dispatch, deeper initialization and application-loop behavior remain unresolved. No canonical admission or C implementation.
