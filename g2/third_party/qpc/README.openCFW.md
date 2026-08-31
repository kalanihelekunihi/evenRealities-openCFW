# QP/C 6.5.1 EM9305 source snapshot

This directory contains the exact public Quantum Leaps QP/C sources needed by
the shipped EM9305 QK/QF/QEP cluster. They come from the official QP/C commit
`416dcec8820b9cdb5827497e645d0d9375db53c6` (release 6.5.1). Each upstream
file retains its GPL-3.0-or-later/commercial dual-license notice; openCFW uses
the GPL-3.0-or-later option. The complete, canonical FSF GPL version 3 text from
`https://www.gnu.org/licenses/gpl-3.0.txt` is retained in
[`LICENSE`](LICENSE) and authenticated by `verify_snapshot.py`.

The `ports/em9305` headers are openCFW configuration/ABI glue derived from the
authenticated image: 16 active priorities, two event pools, no QF tick rates,
16-bit signals/event sizes/pool sizes and counters, 8-bit queue counters, and
saved 32-bit ARC critical-section state. Interrupt and ISR-context operations
are explicit external providers so portable code contains no invented
hardware implementation.

`verify_snapshot.py` pins every imported file, checks release/license/config
facts, and compiles all eight portable translation units with the host C
compiler. The reviewed GCC 16.1.1 ARCv2-EM toolchain now also compiles those
eight units plus two OpenCFW port units and links them into a deterministic
relocatable ARC component with no undefined symbols or runtime imports; the
checked receipt is
`tools/manifests/em9305-qpc-component-build-summary.json`. The official
controller blob remains the package provider until placement/redirect records
are authenticated and authorized hardware validates scheduling, interrupt,
UART, voltage-monitor, and radio timing.
