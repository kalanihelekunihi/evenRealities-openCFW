# R1 software-TWI GPIO provider closure

The six existing Nordic GPIO wrappers now participate in relocatable
composition. Their delay callbacks were moved unchanged to `sdk_delay.c`,
which remains excluded. This separates the checked register-access contract
from the unresolved busy-loop timing contract; it does not qualify either
translation unit for a byte-identical firmware build.

Direct execution of the locked stock application and compiled wrappers passes
2,112 comparisons. All four bus-specific stock callback sets were exercised
for low, high, output, input, release and read operations across pins 0–47.
Input configuration covers pull encodings 0, 1, 2 and 3; read tests use zero,
all-one and alternating input patterns. The comparison checks ordered MMIO
reads/writes and read-pin return values. Testing the reserved pull encoding
does not recommend using it on hardware. These are emulated accesses, not
physical pin or electrical validation.

Callback locations came from historical scatter-output evidence, then were
executed directly from the hash-locked application at their native addresses.
The current pass does not repeat scatter loading or assume that historical
addresses establish source admission. All nine compiled function bodies are
byte-for-byte unchanged by splitting the existing provider. The final objects
also pass the earlier 186 busy-delay and 186 no-countdown callback comparisons.

The complete source build compiles 487 application and 74 bootloader units
and composes both payloads without duplicate strong symbols. Six application
imports resolve to the GPIO-only object, reducing the count from 254 to 248;
bootloader imports remain 34. No aliases, fixed addresses, vendor HAL changes
or source-plan entries were added. Delay providers and their three imports
remain excluded from composition.

[twi-gpio-review.json](twi-gpio-review.json) binds the report, manifest, source
and object hashes, stock callback addresses, split-body comparison, execution
coverage and exact import delta. Full traces and probes remain under ignored
`build/goal-r1-twi-gpio/`. Final firmware linking, complete source identity and
physical bus timing remain open.
