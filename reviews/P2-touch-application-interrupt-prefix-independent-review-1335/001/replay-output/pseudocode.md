# Application prefix with original interrupt registration

Actual A2A8 now executes A214 and A274 without helper replacement. Supplied startup vector RAM is copied from the authenticated first192flash bytes and VTOR is set to20000400, matching separately recovered reset preconditions. Original descriptor atB0E8 specifies interrupt7; the actual chain programs its priority and exchanges vector slot23 at2000045C with callback3625. Assertions require both deeper helper entries and final vector word.

Three deeper peripheral calls, four deeper storage calls and three later application dependencies remain controlled. All prior clock/SysTick/object/settings/descriptor assertions and arrival3D50 remain. This supplied-state replay establishes instruction behavior; physical interrupt dispatch and active hardware VTOR observation remain unresolved. External clock tables remain synthetic. No canonical admission or C implementation.
