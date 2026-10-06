# Timer expiration and rollover recovery

## Provenance

The source target is the locked `g2-2.2.6.10` bootloader payload `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, 148,599 bytes, SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, mapped at `0x00410000`.

| Stock routine | Loaded address range | Bytes | SHA-256 |
|---|---:|---:|---|
| Expire head timer | `[0x00419406, 0x00419444)` | 62 | `98129c991462051f3b3a4ef010ab8f4f7f5a616f5c67f6e09dc36fb613f2f5d2` |
| Rollover/drain and swap | `[0x0041965c, 0x00419684)` | 40 | `73dfaffcae66eb30a9cb1ddac90c5a2f310265191e8aa24645b163872764f36c` |
| Reload helper (upstream-owned) | `[0x004193de, 0x00419406)` | 40 | `1b60b47c1229f8613d7b65051d7915718a88fefceea6f23bb6726ff3f09657ff` |
| Sorted insertion (upstream-owned) | `[0x00419508, 0x00419546)` | 62 | `b2b89293e8e3c562f4fb2cc66a5d4c5491ccc651411b45d00fc9f83c4504c1d8` |
| List unlink | `[0x0041b5a8, 0x0041b5ce)` | 38 | `e1ca0b525effd60568d00101c08010374cebfd3c80ee6ade4fec4da54bcb8794` |

The two timer globals are confirmed by the stock literal pool: the word at `0x00419714` is `0x20027178` (current timer-list pointer); the word at `0x00419718` is `0x2002717c` (overflow timer-list pointer). Both instructions and literal values were read from the locked image, not inferred from decompiler names.

## Recovered behavior and ABI

`opencfw_bl_timer_expire(base, now)` selects the first timer-list item from `*0x20027178`, reads that item's owner pointer at item offset `+12`, and unlinks the timer's embedded list item at `timer+4`. Stock callers establish the arguments:

- At `0x419458`, the timer service captures the selected deadline as `base`, samples current tick as `now`, and invokes expiration only when `now >= base`.
- At `0x41965c`, rollover invokes expiration with the first list deadline as `base` and `UINT32_MAX` as `now`.

The flag test is exactly `LDRB timer[0x28]; LSLS #29; BPL`, which tests bit 2 (`0x04`). When set, expiration calls upstream-owned `opencfw_boot_timer_reload(timer, base, now)`. When clear, it clears only bit 0 of the flag byte. It then calls the function pointer at timer offset `+0x20` with `timer` in R0.

`opencfw_bl_timer_rollover()` repeatedly expires the head of the current list with that head item's deadline and `UINT32_MAX`, until the list count reaches zero. It then swaps the current and overflow list pointers at `0x20027178` and `0x2002717c`. This drains every timer in the old current list regardless of its numeric deadline and moves any reload reinsertion into the other list before the swap.

The timer-object callback ABI is `void callback(timer *)`. Timer creation commonly puts the stock dispatcher address `0x41639b` in timer offset `+0x20` and a tagged serialized callback-record pointer in timer word 7. The dispatcher calls `opencfw_boot_timer_id_get(timer)`, clears the record's low allocation bit, then invokes the serialized callback with the record's argument word. The existing source dispatcher and `task_entry_adapters.S` preserve that boundary; this timer fixture instead uses synthetic Thumb callback functions that record the incoming timer pointer. Their callback bodies are deliberately outside this component.

## Evidence and limits

`verify_timer_expiration.py` runs the original Thumb instructions and compiled Cortex-M4 source against the same synthetic timer lists and callback functions. It compares full state for eight timer-flag values and a two-item rollover with a pre-existing overflow item: 9 cases, 278 distinct original instruction bytes traced, PASS. The fixture links actual source for reload `0x4193de`, insertion `0x419508`, and list insert/unlink; it therefore tests periodic catch-up reinsertion and callback ordering as well as rollover. The image hash, ELF hash, source hashes, per-case trace, and resulting RAM are recorded in `comparison.json`.

The source files are `g2/components/bootloader/thread_creation/timer_expiration.c/.h`. The test-only linker script places a callable test ELF outside the firmware load range. No device, flash, scheduler, physical timer, IRQ delivery, or serialized callback record is exercised. The test shows original/source agreement for these routine paths; it makes no source-completeness or whole-image byte-identity claim.
