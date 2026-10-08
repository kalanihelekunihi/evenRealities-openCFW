# Startup initializer: calibration cache and registered hooks

Locked bootloader SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, Apollo510 Cortex-M55 target, little-endian Thumb at `0x410000`. Offline instruction tests use Unicorn Cortex-M33, not a physical Cortex-M55 model. The remaining selected initializer is `41c4b4..41c7de`, 810 original instruction bytes. [Readable reconstructed orchestration](reconstructed_initialize.c), [original disassembly](disassembly.txt), [bounded comparison](orchestration-comparison.json).

## New native prerequisites

Eight independently reconstructed helpers are in `g2/components/bootloader/initializer_callbacks/startup_initialize_leaves.c/.h`. [Direct receipt](comparison.json):956 comparisons PASS;230/230 original body bytes visited. Setter `41c9ca..41ca08` packs the LOW THREE BYTES of its input into shifts8/4/0, preserving overlapping/out-of-range values. It rejects low byte3 when SCR (`e000ed14`) bit16 or17 is set. It writes `e001e300`; the register's implementation-specific physical interpretation is unresolved. Getter `41ca0c..41ca2c` returns three masked TWO-BIT fields at shifts8/4/0; setter/getter do not round-trip arbitrary input bytes. A mutant that narrows setter input to two bits is rejected (input4 stock writes1024, mutant0).

Hooks `41cdca/41cde0/41cdfa/41ce10/41ce26/41ce3c` read offsets20/24/28/30/34/38 from table `20026e38`. Absent hooks return0; present hooks return callback status. Hook24 truncates both arguments to bytes only when invoking a callback. These synchronous wrappers do not establish asynchronous retention or scheduler drain.

## Initializer behavior and data

The initializer clears `4000885c` bit2 conditionally on bit1. Unless `200271a3` is set, it invokes debug release and power-leave28 before clearing `40020250` bits0..3. It applies the sleep fields from word `434160`, sets `4002021c` bit0, and conditionally queries/enables power29 from `400201bc` bit3. If marker `200267f8 != 1f01600d`, two INFO requests `(1,210,1,2002682c)` and `(1,245,1,2002683c)` run. A nonzero status from either returns immediately; most later child statuses are ignored.

Calibration cache flag `200271a8` guards one-time register-field capture. Cache words `2002704c..20027088` contain the following captures:

| Destination | Register | Extraction |
|---|---|---|
|2704c/27050|40020044/4002004c|low7 bits|
|27054|40020374|bits29..30|
|27058/2705c|40020080|bits10..13 / low10 bits|
|27060/27068|4002036c|bits20..25 / bits26..31|
|27064/2706c|40020088|low6 bits / bits18..23|
|27070|400201b0|whole word|
|27074/27078|40020344|bits25..29 / bits11..15|
|2707c/27080|4002034c|bits25..29 / bits11..15|
|27084|40020358|bits8..12|
|27088|40020354|bits17..21|

All destinations have prefix `200`; no physical units are asserted. Correction of2705c requires `40021108[5:4]==3` and revision (`4002000c` low byte)33 with nonzero variant (`20000098`), or revision>=34. Add7 for rev33/variant>=3, rev34/variant1 or rev35/variant0. Otherwise add6 for rev33/variant<3 or rev34/variant0. Other qualifying combinations retain the raw field. Flag is set after capture; later invocations skip recapture. Firmware revision>=34 also sets byte2000009c and finally ORs6 into400211c8.

Before final hooks it sets4002037c bit30 and40020380 bits16/12. It saves/disables interrupt state, calls hook20 and hook24(0,byte200271a5), restores original PRIMASK, then calls hook30 and child41acb2. The distinction matters for CFW callbacks: first two execute in the modeled disabled region; hook30 executes after restoration. This is instruction ordering, not proof of real interrupt behavior or safe concurrent replacement.

## Validation boundary and next work

816 comparisons PASS with all810 original initializer bytes visited. They cover chip revisions32..36, variants0..4, gate0/3, zero/all-one register seeds, cache set/unset, callbacks absent/present, initial interrupt state, both INFO early errors, power29 query branches and debug-skip branches. Sleep setter and three hook wrappers execute natively. Twelve children are explicit cuts:42252e,41c17a,41c2d8,41bf84,41b918,41c320,421548,41ce52,41bbd0,41be36,41b8ec,41acb2. Their order and selected arguments/synthetic responses compare; their native effects are NOT established by this orchestration suite. No SRAM write recorder is installed.

Standalone source modules and input hashes are preserved under `g2/build/bootloader-completion/startup-initialize-analysis/`. This work is not linked into promoted761be470 and does not reduce its10 OTA boundary count. The next useful closure is the local runtime initializer41ce52, followed by binding already recovered children and retesting with native providers. This is an analysis boundary, not a missing external input. Physical calibration units, hardware acknowledgement, scheduler/IRQ/task drain, complete source and byte identity remain unresolved.
