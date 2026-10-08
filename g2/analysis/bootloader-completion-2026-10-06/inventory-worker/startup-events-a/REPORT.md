# SPOT startup event A reconstruction

This folder contains fixed-address C reconstructions of the stock Apollo510 SPOT callback at `0x42a878`, state classifier `0x42a550`, deepsleep mutation `0x42a08c`, trim updater `0x42a4bc`, and its call-free ton/trim leaf `0x42a1bc`. The ABI header, offline stock/source runner, test-only transition providers, and generated comparison receipts are in this folder.

## Evidence and build

The locked input is `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`. The callback extent is `[0x42a878,0x42ab6e)`, exactly 758 bytes, SHA-256 `83deb1cccedcf7dab0c986deaacc2f94baea6d1f74b7e7e387fbdb9f77527079`.

The public callback prototype and stimulus values follow Ambiq's Apollo510 `am_hal_spotmgr.h` enum and declaration (`am_hal_spotmgr_power_state_update(am_hal_spotmgr_stimulus_e, bool, void *)`). The local snapshot has seven fields: four 32-bit power fields at `+0x00..+0x0c`, followed by temperature, CPU, and GPU bytes at `+0x10..+0x12`. Its fields occupy 19 bytes and its aligned C `sizeof` is 20; compile-time offset assertions guard the observed offsets.

Build with `make -C g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-events-a event_a.elf`. The source is built for the Cortex-M33 Thumb-2 baseline. Temperature classification compares IEEE-754 binary32 bit patterns to the authenticated stock boundaries, avoiding an emulator-only FPU instruction gap.

Run the differential with:

```sh
/Users/kalani/.local/share/opencfw/venv/bin/python \
  g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-events-a/verify_event_a.py \
  --elf g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-events-a/event_a.elf \
  --output g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-events-a/comparison-descendants.json
```

The runner authenticates the locked image and exact callback bytes before execution. The current descendant run passes all 150 fixtures, compares status, PRIMASK, argument writes, selected SRAM globals, power-register values, and child boundary values, and visits 740 of the callback's 758 bytes. The 18 unvisited bytes remain unexercised. It also visits 770/782 bytes of the 42a550 state classifier, 272/272 of 42a08c, 138/148 of 42a4bc, and 118/232 of 42a1bc. These are dynamic instruction-byte coverage counts, not proof that unvisited branches are correct; the receipt contains per-range counts.

The table +4 routing is corroborated by the separately passing stock/source installer differential: revision/variant `33/2 -> 0x42d563`, `34/2 -> 0x42ba01`, `35/2 -> 0x42a879`, `36/0 -> 0x42a879`. This module does not modify shared tables.

## Direct-call frontier and limits

The stock callback's direct leaf calls to `0x41b8ec` critical-save, `0x427e0c` temperature classifier, and `0x42a19c` internal power-domain helper execute as native stock code on the original side and in existing/reconstructed source on the source side. Reconstructed `0x42a550`, `0x42a08c`, `0x42a4bc`, and `0x42a1bc` likewise execute as native original/source bodies; these are not replaced by stock-code fallback in the source machine.

The state selector `0x42a2b4` and temperature-transition walker `0x42a43a` now have source C in `startup_event_a_transitions.c`. The source selector and locked stock selector match on all 400 pairs of documented states 0..19; the source walker matches the stock walker over the same 400 pairs with the authenticated installed callback table at `0x20000158`. Receipt: `comparison-transitions.json`. This receipt authenticates the locked image and the 28-byte matrix, and records the actual 27 callback targets from the passing selector-table receipt. Selector 24 is closed against stock `0x42a030` (`BX LR`); its source preserves incoming R0 as required by that instruction. IDs 25 and 26 are also `BX LR` in stock but are unreachable for documented state inputs.

Selector 8 is a reachable 212-byte target at `0x428bb0`. The timer-disabled source body in `startup_event_a_sequence8.c` retains its separate stock/source receipt of 400 target/current pairs. The full active-timer entry is in `startup_event_a_sequence8_timer.c` under the distinct symbol `event_a_transition_sequence_8_timer_native`; its strict differential receipt `comparison-sequence8-timer.json` passes 24 fixtures linked into a successor ELF separate from the frozen root candidate. Locked instructions confirm TIMERCONTROL bit 0, status bit 30, status polling before each 1-us delay, a 60-delay cap, and ISR entry at `0x42a04a`. The verified native timer-service source handles callback states 2 and 7 through sequence targets `0x428378` and `0x428a94`, then releases via the native timer-stop path. Tests compare ordered writes, return state, interrupt mask, stack pointer, and ROM delay inputs, and include ready and timeout paths with state bytes `0x1a`, 2, 7, and 26.

The second ELF `event_a_native.elf` links the main callback to native source selector/walker, callback 8, callback 24, trim, and critical-save code. Its 150-fixture stock/source differential passes in `comparison-native.json`, with 740/758 bytes of the main callback visited. The actual installed callback table is authenticated from `scatter-selector-table.json`; callbacks 0..7 and 9..23 are explicit cuts before their first target instruction, with no substituted return/status. Callback 8 and the no-op callback 24 execute native source. The older 50- and 150-fixture receipts remain unchanged and retain their former test-provider boundary.

`startup_event_a_sequences_0_2.c` contains source bodies for actual trace targets `0x427e84` and `0x428240`, exported as `event_a_pcm22_transition_sequence_0` and `_2`. They import root-owned native timer start/stop/service, I-cache, delay, cache-enable, and trim helpers. The implementation was corrected against locked Thumb instructions: TIMERCONTROL enable is bit 0; sequence 2 takes VDDf from profile base `+0x50`; and sequence 0 performs the two distinct tempco `[13:10]` then active `[9:0]` writes to `0x40020080`.

`verify_event_a_root_handlers.py` authenticates the locked image, actual selector table, and 368-case root-reachability receipt, then rejects any source-side execution through locked code. Its strict differential passes 22 fixtures against the parent-linked native candidate in `comparison-root-handlers.json`: selectors 0 and 2 with the exact root vectors; timer on/off; I-cache on/off; timer service state byte `0x1a`, `2`, `7`, or `26`; and the selector-0 target-equals-cached fast branch. It compares R0, PRIMASK, SP, ordered SRAM/MMIO writes including values, and captured ROM delay inputs. No success-only substitutes are used for native helper calls. The controlled external boundary is resident ROM delay at Thumb address `0x41`, whose input is captured and whose void return is modeled. Selector IDs 14 and 18 are separately owned; ID 24 preserves incoming R0 as stock does.

MMIO/SRAM values are deterministic Unicorn fixtures; this does not claim physical SPOT or scheduler behavior. No MetaWare compiler is available, so the C output is not claimed byte-identical to the locked callback or a complete firmware rebuild.
