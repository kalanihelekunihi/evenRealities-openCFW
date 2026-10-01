# Application prefix with actual object initialization

Actual 3658 and its 404C/A9D4/3EE8 chain now execute within startup, producing the 80-byte object at 20000940 with first halfword 1000 and remaining bytes zero. This uses the settings timeout established by actual 395C under explicit deeper storage controls. All previous register, clock, SysTick, callback, descriptor and settings assertions remain; stop3D50 is reached.

Four deeper storage calls and five later application dependencies remain controlled. External clock tables remain synthetic. Physical storage, interrupt dispatch and application loop behavior remain unresolved. No canonical admission or C implementation.
