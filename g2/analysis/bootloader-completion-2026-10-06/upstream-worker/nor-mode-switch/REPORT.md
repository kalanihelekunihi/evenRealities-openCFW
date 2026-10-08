# NOR mode and address-mode providers

## Current source

This work adds readable source for three locked routines:

| Locked routine | Source entry | Behavior established by code and differential |
|---|---|---|
| `0x420c5c` | `opencfw_provider_420c5c` in `g2/components/bootloader/nor_mspi_power/serial_mode_switch.c` | Checks the active-handle word at `0x200270dc`; delays; reads status with instruction `0x05`; compares status bit 6 to the byte-truncated mode and checks reserved bits `0x3c`; otherwise WREN, changes bit 6, clears bits `0x3c`, writes with instruction `0x01`, delays, and verifies. Firmware logs identify this as the QE-bit setter. |
| `0x420800` | `opencfw_provider_420800` in `g2/components/bootloader/nor_mspi_power/xip_address_mode.c` | Clears a five-byte local region, reads status with instruction `0x15`, and returns the raw read error or whether input bit 5 is set. It logs status-read failure and the 3-byte-mode message. The bit test follows the stock `LSL #26` sign test exactly. |
| `0x420890` | `opencfw_provider_420890` in the same file | Checks the active-handle word; checks the first delay result; WREN; sends command `0xb7`; performs another delay whose result is ignored; checks status via `0x420800`; if the helper returns zero, logs verify failure and returns 1; otherwise WRDI and returns its status. |

The `0x420800` error result is nonzero, so its caller in `0x420890` treats a failed status read as if the mode check passed and proceeds to WRDI. This odd branch behavior is retained and covered by the differential.

## Verification

Both source files compile as freestanding Cortex-M4 Thumb ARM objects using the repository's installed Clang and link with the isolated test linker scripts. The source ELF is executed against the locked bootloader in Unicorn with deterministic synthetic lower-call callbacks.

`make -C g2/analysis/bootloader-completion-2026-10-06/upstream-worker/nor-mode-switch verify` passes all 16 `0x420c5c` cases and compares return, lower-call events and inputs, mutable status bytes, logger text/line, SP, and callee-saved registers. It covers null handle, initial status error, fast success, WREN and write errors, reserved-bit clearing, verification error/mismatch, and mode values 0, 1, 2, `0xff`, and `0x100`. The run traverses 414 distinct original instruction bytes. Source ELF SHA-256: `93994cf07a4a5e583129b490ad8df21d2eba3b3a92f5c7c197c92b9b22b67d60`.

`make -C g2/analysis/bootloader-completion-2026-10-06/upstream-worker/nor-mode-switch -f Makefile.xip verify` passes all 15 cases for `0x420890` and direct `0x420800`. It compares result, lower calls, ordered logs, SP, and callee-saved registers across handle, delay, WREN, command, status-read/bit, and WRDI branches. The run traverses 340 distinct original instruction bytes. Source ELF SHA-256: `8584cf08e1fa6c2a6d10bebb1a9ad13d9f13c96a44b6559ec0e4bc3fcb575ae1`.

## Provider edges and limits

The linkable production symbols use the already named dependencies: `opencfw_bl_nor_read_delay`, `opencfw_provider_4205f4`, `opencfw_provider_42069e`, `opencfw_provider_420984`, `opencfw_provider_4209c4`, and `opencfw_bl_log`. Their tests intercept equivalent interfaces for determinism; the isolated tests do not establish their combined full-source execution in these two paths. `0x426c10` is an original-only byte-clear helper used by `0x420800`; the C source initializes its local region directly, so the differential compares its resulting behavior and not the implementation of that helper.

The active handle and status bytes are synthetic. Delay results are raw provider results, not calibrated units. The tests exercise no attached flash, MSPI hardware, XIP execution, power sequencing, or hardware timing. The source was reconstructed from the locked bootloader instructions/decompilation; public HAL code was not substituted for these private flash-driver routines. Full image integration and byte identity are not claimed.

## Automatic timing scan source

Added `g2/components/bootloader/nor_mspi_power/timing_scan.c` for locked scan entry `0x420002`, including source implementations of the adjacent bit-window helpers `0x41ff60` and `0x41ff74`. It runs 36 profiles × 32 fine-step settings. For each trial it copies profile bytes 0–3 and 5 into a six-byte control record, writes the fine-step index at byte 4 and literal 8 at byte 5, calls control request `0x10`, and calls the source JEDEC helper with command `0x9f`. A returned ID equal to `0x2539c2` sets that trial's bitmap bit. The scan selects the profile with the largest low-end run of passing bits (keeping the first profile on ties), computes the stock longest-window center with the original wrap adjustment, logs the selection, writes bytes 0–3/5 and the center at output offsets 0–5, and returns zero.

`make -C g2/analysis/bootloader-completion-2026-10-06/upstream-worker/nor-mode-switch -f Makefile.scan verify` passes six original/source cases. It executes the stock scan, stock JEDEC helper and stock bit-window helpers against the separately compiled scan and existing source JEDEC helper. The cases cover no passing bits, all passing bits, ignored HAL-control errors, tied prefix scores plus a wrap-edge window, several disconnected windows, selected JEDEC transfer failures, and the authenticated initialized table. Each case compares 1,152 control records and transfer calls, complete ordered logger/callback events, return/output bytes, stack, and callee-saved registers. The run covers 682 distinct original instruction bytes. Source ELF SHA-256: `10809ff9369d8fd87b7c988621cbb4e1ad4d34cbdc4f30dba4bf00ababeffe61`.

The profile table's exact producer is now traced. Scatter record `0x433104` points to the authenticated 625-byte stream `0x4341c0..0x434431`, which locked helper `0x415326` expands into `0x20000000..0x2000055b` (1,371 bytes). The table at `0x20000244` is output offset `0x244`, length 216 bytes. Its SHA-256 is `a26d40aacdbb0889ec7da60e94af64373ba35610ca63a92b0555b718cdeae182`; the full expanded block SHA-256 is `e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843`. The table has four groups of nine profiles: `[1, groupA, groupB, setting, 1, 0x20]`, where each group selector is 0 or 1 and `setting` ranges 1 through 9. `extract_profile_table.py` reproduces the fixture by executing the locked decompressor over the locked scatter record/stream. This locates the exact data without embedding firmware instructions or using a guessed hardware default; source generation of the encompassing compressed data block remains a separate source-build task.

`opencfw_hal_mspi_control` and the lower status-transfer/MMIO behavior remain synthetic callbacks. A failed JEDEC read is logged and does not set a scan bit. This establishes the algorithm and actual profile inputs, not that flash accepts a profile or any physical timing/calibration behavior.

## Wrapper-level scan integration

`make -C g2/analysis/bootloader-completion-2026-10-06/upstream-worker/nor-mode-switch -f Makefile.wrapper verify` links the stock-ABI `nor_timing_wrapper.S`, existing `nor_commands.c` timing core, the new scan, and source JEDEC helper into one ELF. Three original/source cases pass through `0x4201ba` and the full 36×32 scan, covering all-passing/all-missing samples, wrap-edge center selection, and two different nonzero untouched caller-stack tails. It compares the full scan transaction sequence and logs, global eight-byte timing result, return, SP, and callee-saved registers. The run covers 744 distinct original instruction bytes; linked source ELF SHA-256 is `156c5dedb1c4b346dd0552b06ced1de96780cb745392be69421bd650f8999243`.

The wrapper deliberately copies eight bytes from its local stack although the scan initializes six bytes. Bytes six and seven remain caller-stack data; the tests seed those two bytes on both machines and compare them, rather than assigning undocumented values. This behavior remains a source-call-context dependency when the wrapper is invoked by another source caller.
