# I2S power control, snapshots and uninitialize

**868 PASS original/independent comparisons**:804 selected power cases,32 control-dispatch cases,32 uninitialize cases. A further **8 original-only probes reach the expected external ROM boundary**, not full-delay PASS cases. [Independent C](../../components/audio/i2s_power_offline/power.c), [results](results.json), [delay probes](delay-boundary-results.json), [instructions](original-disassembly.txt), [provenance](provenance.json).

## Recovered power sequence

`0x590648(handle, mode, backup)` reads module from handle+4 before its NULL test, requiring a mapped non-NULL handle. Marker `handle[0] & ~0xFE000000` must equal0x01125125. Mode/backup are narrowed to uint8. Mode0 is the power-on/restore path; modes1/2 share power-off/optional-save; other modes return6. Mode0 with requested restore but handle byte+8 zero returns7. Invalid marker returns2.

| Mode | First-party behavior |
| --- | --- |
| 0, backup0 | Calls peripheral-on for module+31, ignores that return, returns0 if provider returns |
| 0, backup1 | Calls peripheral-on, restores12 registers, acquires clock group4 for peripheral29/30; propagates acquisition failure. Active byte+0x60 triggers source-group acquisition and reconfiguration. Second failure releases group4 before returning. Successful path clears snapshot marker+8 |
| 1/2, backup0 | Calls peripheral-off for module+31, ignores that return, returns0 if provider returns |
| 1/2, backup1 | Reconfigures request0x217, releases group4 and optional active source group, saves12 registers, sets marker+8, then calls peripheral-off |

Snapshot values live at handle+0x0C..+0x38. In order, peripheral register offsets are `{0x48,0x40,0x44,0x54,0x100,0x4C,0x10,0x30,0x300,0x200,0x60,0x64}` from `0x40208000 + module*0x1000`. Saved offset0x48 is masked with0x11; other values are copied whole. Snapshot storage persists through uninitialize; no memory allocation/free occurs in these wrappers.

`0x5900CE` safely checks NULL before accessing the marker. Success clears marker bit24, retains only high-byte status bits, sets module word+4 to0, returns0. It does **not** itself clear enabled bit25, free storage, poll DMA or issue power commands. Earlier stop callers clear bit25 separately. Other snapshot/control fields remain unchanged.

## Provider and test boundaries

Power-on/off copy authentic four-word table rows through `0x47EF18`: module0 index31 `{0x4002100C,0x40,0x40021010,0xC0}`, module1 index32 uses command mask0x80 and the same status mask0xC0. Real register/clock peers execute. `0x480312` dispatches the optional platform callback at `0x20073274`, narrowing action/enable to bytes; NULL returns0 without altering supplied metadata. Tests execute that real NULL branch, and separately compare non-NULL dispatch arguments while stopping before chosen user child0x53C2A4. A non-NULL callback's behavior/result is not fabricated.

Fixtures cover module0/1, valid marker, snapshot marker, active flag, mode0/1/2/3 plus byte aliases256/257, backup0/1, initial power command, and allowed-clock flag. Config0x217 exercises unsupported source-group failure/rollback;24 additional cases use0x208 for the successful active restore branch. Busy-status cases stop at retry delay0x4807A0 entry. Independent C covers the first-party wrapper/control dispatch; original peripheral/clock providers are shared. Handles, used call arguments, ordered MMIO writes, clock membership, result or boundary and PRIMASK agree. SCB/power/status values and callback absence are **synthetic passive fixtures**, not observed device state.

The retry provider0x4807A0 was then run separately with an ARMv8-M Cortex-M33-compatible FPU profile. Inputs1/2/5/100 and two clock selectors execute original arithmetic and branch to **resident ROM0x40**, producing an unmapped fetch. No trampoline, trap, copied opcodes or fake delay return is supplied. The locked raw OTA maps0x438000..0x794324 and lacks these ROM bytes. Need an authenticated resident-ROM image or a defensible external ROM behavior contract to execute that dependency. Numeric retry inputs are not promoted to a verified physical duration.

This closes selected power/snapshot/uninitialize software ordering. It does not prove physical shutdown, clock readiness, DMA completion or retry timing. Dirty file-close still independently needs mounted filesystem/cache/block state, and live lifecycle claims need scheduler/device evidence.
