# Application prefix with actual peripheral initialization

Actual 3678 now executes its four deeper initialization calls through explicit return-only controls, then stores callback3701 at20000930, writes interrupt bit7 atE000E280/E000E100 and sets bit31 at40250000. The original context byte determines the additional bit8 OR at4025006C. Four deeper peripheral calls and four deeper storage calls remain controlled, followed by three later application dependencies.

The prior descriptor links, object/settings, clock, SysTick, callback and register assertions remain and stop3D50 is reached. No physical peripheral operation, interrupt dispatch, real storage or loop completion is claimed. External clock tables remain synthetic. No canonical admission or C implementation.
