# Startup with original row-enable predicate

Original 7DDE executes for rows0,1,2 inside original71C8. Authenticated initialized row flags have bits1 and2 set, so all three conditional5CAC calls are now reached. Those calls remain explicitly controlled with zero statuses; their exact row indices are checked. This replaces the earlier controlled predicate responses that suppressed these calls.

All inherited startup state checks and exact remaining boundary sequence pass through arrival at3D50. Other activation helpers, storage and later application dependencies remain controlled. SyntheticMMIO and externalclocktables remain explicit. Physical meanings and whole-firmware coverage remain unresolved. No canonical admission or C implementation.
