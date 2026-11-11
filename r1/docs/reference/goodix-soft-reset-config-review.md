# Goodix stock software-reset configuration

The selected Goodix demo kernel previously inherited the vendor default `__SUPPORT_HARD_RESET_CONFIG__ = 1`. That chooses hard-reset calls and two unimplemented reset-pin hooks. The locked R1 instead uses software reset. REA observes `Gh3x2xDemoInit` calling `GH3X2X_SoftReset` at `0x2d9be`, targeting `0x2accc`. Direct instruction checks against the same authenticated application also find software reset at `0x2d6be` (configuration switch), `0x2dd54` (interrupt processing) and `0x2e486` (sampling startup).

`r1/src/config/goodix/native_demo_reset_config.h` retains the kernel's pinned vendor configuration and changes only that reset setting to zero. The manifest generates `gh_demo_r1.c` with that header, and changes the existing generated demo-user unit's include to the same header. Pinned vendor sources remain unchanged. The generated kernel unit has a local include flag so the original kernel configuration resolves without changing other profiles.

The source audit proves:

- All 573 other objects are byte unchanged. No profile or unit count changes.
- `Gh3x2xDemoInit` changes its reset policy. Four other kernel functions retain identical instruction bytes with only HardReset-to-SoftReset call relocations changed. These include an engineering-mode helper whose native entry is not independently mapped; its emitted policy follows the same configuration macro, without receiving stock coverage credit.
- The other 39 kernel functions and 22 retained demo-user functions keep their bodies and relocation targets. Only the two hard-reset demo-user functions disappear.
- The resolved macro sets differ only in the reset setting and the new include guard.
- All 575 units compile without failures or duplicate strong symbols. Application imports decrease from 175 to 173, removing exactly `gh3026_reset_pin_init` and `gh3026_reset_pin_ctrl`; bootloader imports remain 34. No imports are added.

Five official qualification profiles compile the generated kernel unit and select no regions. This corrected candidate is not admitted to the exact source plan. The canonical hybrid remains byte-identical to the locked application, using 3,905 source-built bytes, 642,255 stock fallback bytes and 248 resource bytes. Compilation and callsite/configuration evidence do not prove complete initialization behavior, physical sensor operation or full-source firmware completeness. The interrupt-pin hook and other possible configuration differences remain separate work. G2 gates are unchanged.

The current normal report is `build/sources-goal-r1-goodix-soft-reset-final/report.json`. [Machine-readable evidence](goodix-soft-reset-config-review.json) binds the REA capture, raw call instructions, source audit, manifest, qualification and hybrid build by hash. Probes remain under ignored `build/goal-r1-goodix-soft-reset/`.
