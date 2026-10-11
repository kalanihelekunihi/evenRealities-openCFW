# G2 C firmware candidate build

Run `python3 g2/firmware_c/build.py --image apollo_main` from the repository.
Omit `--image` to build every available image candidate. The output is
`g2/build/c-firmware/latest/receipt.json`, compiler logs and source-built
relocatable objects. Main and Audio are compiled together as subgraphs of
the official Apollo MAIN image; Bootloader remains a separate target.

`--include-experimental` additionally compiles and composes the newly reduced
Main logger, UART IRQ and full power control flow. Their product state and
physical lower contracts remain explicit imports; the receipt lists these
units as experimental even when compilation and relocatable linking succeed.
It also composes the scheduler-delay and classifier adapters. The CASE full
command graph builds as a distinct experimental archive and relocatable,
preserving its separation from selected providers.
Bootloader experimental composition includes the TLSF diagnostic printf and
floating-log entry candidates; their stock output and floating domains still
need qualification. Stable exclusions keep both outside the selected archive.

The coordinator rebuilds C-SKY DSP source with the retained qualified compiler
and records source and included-header hashes. With `--include-experimental`
it also builds two GX8002 application helpers, preserving their four product
imports. The pinned public ARC GNU 2026.03 toolchain also compiles the EM9305
queue unit to verified ARC EM ELF32. Experimental mode also compiles recovered
scheduler control flow with explicit vendor instruction/assertion imports.
The codec experiment includes five additional board/UART C bodies with explicit
board constant and gain-table data imports. These remain candidate subsets of
the controller and codec images. The ARC build does not establish the producing
EM7D configuration. Restore the ignored
compiler download with `python3 g2/firmware_c/fetch_arc_toolchain.py`; its manifest
records the official release digest and source submodule pin. Docker and the
retained `opencfw/iar-base:10.10.2-local` runtime are required.

`--require-complete` exits with status 2 while any selected image lacks complete
source ownership. Successful candidate compilation alone cannot remove a
gate in `source-gates.json`. The remaining body, initialized-data, startup,
linker and external dependency contracts must be implemented and reviewed.
No official payload or prebuilt executable library is consumed by this
coordinator, and no candidate relocatable is packaged as a flashable image.
