# R1 flash fit: targeted Clang size profiles

The strict R1 application exceeded its 696,320-byte flash span by 31,432
bytes at `build/r1-roundf-strict-pure-c-20261110/app-link/report.json`.
An ignored, current-source probe compiled the 220 largest Clang `-Os`
application objects with the same arguments except `-Oz`. It found 32,725
bytes of positive raw allocated-section savings across those objects, before
final linker garbage collection or address effects. Its commands and ranked
results are in `build/r1-size-current-probe-20261110/`.

The manifest now uses `-Oz` for 25 Clang application units: six CMSIS/FreeRTOS
timer units (`r1-application-19`), 13 ST25/PMIC units
(`r1-application-25`), two Bosch BMA units (`r1-application-40`), and four
upstream/generated Goodix driver units on a new copy of the original Goodix
profile (`r1-application-5-oz`). The other 99 units on the original Goodix
profile retain their flags. No firmware C function or data source was removed.

A fresh source build compiles all 883 application and 82 bootloader units,
with no failures or duplicate strong symbols. Across the 25 changed units,
the strong and weak export names, exported object-data names/sizes, and Arm
ABI attributes agree with the preceding `-Os` build. The only attribute
change is the compiler's expected size-optimization-goal tag. Two new
compiler-helper references (`__aeabi_llsl` and `__aeabi_memcpy`) resolve in
the strict link; the application undefined set remains 37. The strict flash
overflow is now **28,616 bytes**, a **2,816-byte reduction**. The narrower ld
region diagnostic is 21,688 bytes. The current receipts are
`build/r1-targeted-oz-c-20261110/report.json` and
`build/r1-targeted-oz-c-20261110/app-link/report.json`.

`make sources-check` passes (965 R1 units, 752 files, none unbuilt), as does
`git diff --check`. The strict bootloader link still has no undefined symbols
and a valid vector. The application still does not link. Export and ABI checks
do not prove device timing, sensor data fidelity, or byte identity; these
profile changes need behavioral and hardware validation before release.

## Second targeted pass, 2026-11-10

Fourteen more application units now use per-unit `-Oz` and
`-mno-global-merge`. The latter is necessary for SDK variables with pinned
sections: a plain `-Oz` build merged private peer-manager state and failed
the observer's RAM layout check. With global merging disabled, named data
sections, exported symbol kinds and sizes, and Arm ABI attributes match their
previous objects, except for the expected size-optimization attribute. The
two new helper imports, `__aeabi_memcpy` and `__aeabi_llsr`, resolve in the
strict link.

The selected reconstructed code passed stock/C emulator replay: 3,300
peer-observer events, 3,122 Goodix version cases, and 2,176 SpO2 cases over
all 32 FP modes. These checks do not cover physical-device timing or every
input. A full R1 source rebuild compiled 886 application and 82 bootloader
units without failures or duplicate strong symbols. The strict bootloader
links with a valid C vector. The strict application still has 36 undefined
references; its full flash overflow is **25,064 bytes**, down from 30,232.
The authoritative receipts are
`build/r1-oz-no-merge-final-20261110/report.json` and
`build/r1-oz-no-merge-final-20261110/app-link/report.json`.

An ignored substitution probe reported 23,016 bytes of overflow, but its
hashed temporary object filenames bypassed an object-name wildcard in the
recovered linker script. The manifest build's 25,064-byte result is the one
to use. No application executable or byte identity is established.

## NADT reachability pass, 2026-11-11

The full HBA and HRV C adapters leave only `goodix_nadt_calc` unresolved. An
ignored probe retaining the existing typed NADT stream and all three real
classifier cores exceeded the recovered 696,320-byte flash span by 4,920
bytes. Recompiling further application units with `-Oz` and
`-mno-global-merge`, then substituting objects under their original basenames,
put that same build-only classifier reachability link at 691,656 bytes.

The manifest now selects those flags for 80 more application units. The
source build `build/sources-r1-nadt-oz-dfu-c-20261111/report.json` compiles
954 application and 82 bootloader units, with no duplicate strong symbols.
All 80 changed authoritative objects keep the preceding exported symbol
names, kinds and data sizes; the corresponding probe objects also keep their
Arm ABI attributes except the size-optimization goal. The strict bootloader
links. The strict application still has `goodix_nadt_calc` unresolved, and
its partial map uses 680,536 flash bytes. The build-only NADT reachability
link leaves 4,664 bytes for a real adapter and new dependencies. It passes
null inputs and is not firmware. Compiler profiles have not been checked on
physical R1 hardware; semantic and timing parity for these 80 units remain
unverified.

The subsequent NADT public/window views and four-window stream correction
compile in `build/sources-r1-nadt-window-view-final-20261111/report.json`
(955 application, 82 bootloader units). The same full-classifier build-only
reachability link now uses 691,736 flash bytes, leaving 4,584. The strict
application still lacks `goodix_nadt_calc`.
