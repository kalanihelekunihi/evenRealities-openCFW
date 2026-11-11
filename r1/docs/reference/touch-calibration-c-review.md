# C touch model calibration and cached getters

`r1/src/application/board/native_touch_model.c` supplies product-SN decoding
(`0x6a1cc`), the r_size getter (`0x7bac4`), compensation-word getter (`0x7bb04`),
and slider calibration (`0x8e758`). It reuses the existing cached-class handles,
SN reader and IQS model selector. The historical `batcfg` getter names do not
identify their data owners: rec8 reads the one-byte r_size class, and word4c
reads offset 76 in the 124-byte nv_r1 class.

An r_size value 6..15 bypasses SN access. Otherwise, a non-ff first serial byte
allows byte 5 A..J or a..j to select 6..15, defaulting to 13 for other values.
Calibration selects a fresh model table, reads bytes 3 and 4, and preserves the
stock binary32 operations: signed upper-minus-lower times exact `0x43555555`,
lower times that same value truncated to uint32 then uint16 for the origin,
and the separately rounded span divided by 200 for the step. Narrow origin
and step owners at `0x200067c8` and `0x200067d4` match authenticated cold RW;
other bytes in the surrounding native context remain unowned here.

The three captured assembly entry bridges in `native_battery_configuration.c`
are replaced by ordinary C frames. Complete four-byte reads preserve byte,
nonzero-halfword and signed-halfword results. Unwritten private bytes now start
at zero. The SN reader's private 124-byte record also starts at zero while
retaining its marker, copy, optional-length and alias ordering. These initialized
failure/short-read outputs are deliberate C behavior, not equivalence to native
private saved-register or stack garbage.

The [machine-readable receipt](touch-calibration-c-review.json) records:

- 68,238 direct stock/C comparisons, including all 65,536 lower/upper calibration
  byte pairs against both stock and a separately rounded float oracle.
- 2,542 comparisons executing actual C cached-class size checks and critical
  section control against prepared callbacks.
- 752 comparisons through actual C configuration, decoding, calibration, IQS
  ports, transport and registry, checking all twenty configuration records.
- 612 comparisons through the actual C IRQ/reset/recovery/configuration path
  and twelve defined private-buffer fallback checks.
- 84 direct and six cached-class C-only short/failure fallback checks, plus
  thirteen rejected compiled defects and an unmodified cached-class rerun.

Integer and FP callee saves, stack guards, PRIMASK and BASEPRI are checked. Float
proof starts with FPSCR zero; other FP control modes are not claimed. The
[REA byte receipts](touch-calibration-rea-review.json) match the relevant stock
entries and calibration constants to the pinned application.

A diagnostic reproduces an instruction skipped after the compiled copy helper
under Unicorn. The passing probes model standard copy/fill, use real Thumb
provider returns and flush translation caches between reused calls. Calibration,
getters and cached-class control execute their compiled C bodies; no physical
flash or kernel/device operation is implied. Firmware memory code is unchanged
by the probe workaround, which is not a physical fault claim.

The normal build compiles 838 units (756 application and 82 bootloader), with
76 application imports and 22 bootloader linker imports. Three imports close
without adding new ones. All 833 prior nongenerated objects outside the two
changed units remain identical. Within those units, only the SN reader and
three wrapper code sections change; all other allocated sections are identical.

The R1 manifest check passes. Global `make sources-check` still reports the
pre-existing unlisted G2 `resident_rom_thumb_set.S`. Cold RW checks do not prove
final runtime placement; final application linking, physical timing and device
boot remain unverified. Byte identity is not required.
