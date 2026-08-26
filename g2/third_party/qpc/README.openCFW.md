# QP/C 6.5.1 EM9305 source snapshot

This directory contains the exact public Quantum Leaps QP/C sources needed by
the shipped EM9305 QK/QF/QEP cluster. They come from the official QP/C commit
`416dcec8820b9cdb5827497e645d0d9375db53c6` (release 6.5.1). Each upstream
file retains its GPL-3.0-or-later/commercial dual-license notice; openCFW uses
the GPL-3.0-or-later option.

The `ports/em9305` headers are openCFW configuration/ABI glue derived from the
authenticated image: 16 active priorities, two event pools, no QF tick rates,
16-bit signals/event sizes/pool sizes and counters, 8-bit queue counters, and
saved 32-bit ARC critical-section state. Interrupt and ISR-context operations
are explicit external providers so portable code contains no invented
hardware implementation.

`verify_snapshot.py` pins every imported file, checks release/license/config
facts, and compiles all eight portable translation units with the host C
compiler. An ARC target compiler is not installed on the current host, so the
snapshot is not yet admitted as an EM9305 package replacement. The official
controller blob remains the package provider until a reviewed ARC toolchain
can compile/link it and authorized hardware can validate scheduling,
interrupt, and radio timing.
