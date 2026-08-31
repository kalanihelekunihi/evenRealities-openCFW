# TDK InvenSense ICM45608 source snapshot

This directory contains the pristine `src/imu`, `src/Ict1531x`, `src/Invn`,
and `src/invn_mag.[ch]` files from public release tag `1.1.2`, commit
`b79ae575f7f310e5ae2e1164096d1a858bb74662`, plus its root BSD-3-Clause
license text.

This is repository-local research evidence, not a public/compiler input. The
root license does not override file-specific terms: five headers carry notices
that prohibit use, reproduction, disclosure, or distribution absent an express
license, and ten headers contain dense EDMP program/RAM payloads. All 15 files,
the G2 research port, and the clean-room candidate are excluded from the
canonical compiler and community bundle closures.

That release is the public ABI baseline for the G2 stock driver: its transport
contains `read_reg`, `write_reg`, `serif_type`, and `sleep_us` at offsets 0,
4, 8, and 12. The authenticated G2 object stores the sensor-event callback at
device offset 24. Later public releases add a leading context pointer and must
not be substituted without an adapter.

Of the five payload sequences formerly selected by the research route, only
the calibration patch occurs in the official donor image (once); the other
four do not. The post-migration overlay gate requires zero occurrences of all
five sequences.

Run `python3 third_party/invensense-icm45608/verify_snapshot.py` for offline
identity, ABI, feature-surface, and mixed-terms inventory checks.

`g2-compat/Arduino.h` is a separate OpenCFW adapter declaration for the one
`micros()` time callback used by the ICT1531x driver; it is not included in
the pinned upstream aggregate.
