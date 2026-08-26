# TDK InvenSense ICM45608 source snapshot

This directory contains the pristine `src/imu`, `src/Ict1531x`, `src/Invn`,
and `src/invn_mag.[ch]` files from public release tag `1.1.2`, commit
`b79ae575f7f310e5ae2e1164096d1a858bb74662`, plus its BSD-3-Clause license.

That release is the public ABI baseline for the G2 stock driver: its transport
contains `read_reg`, `write_reg`, `serif_type`, and `sleep_us` at offsets 0,
4, 8, and 12. The authenticated G2 object stores the sensor-event callback at
device offset 24. Later public releases add a leading context pointer and must
not be substituted without an adapter.

Run `python3 third_party/invensense-icm45608/verify_snapshot.py` for offline
identity, ABI, feature-surface, and license checks.

`g2-compat/Arduino.h` is a separate OpenCFW adapter declaration for the one
`micros()` time callback used by the ICT1531x driver; it is not included in
the pinned upstream aggregate.
