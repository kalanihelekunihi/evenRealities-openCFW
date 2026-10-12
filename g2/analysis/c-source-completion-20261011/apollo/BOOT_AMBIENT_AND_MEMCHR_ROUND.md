# Boot ambient ABI and memchr source round

Selected source now contains two named Thumb wrappers for native 0x414948 and
0x41b854. The unmount wrapper calls the pinned LittleFS internal-deinit body
through a guarded additive bridge, returns child `r0`, and restores ambient
`r7` into `r1`. The UART wrapper calls the selected UART log-send lower with
`(1, input_r0, input_r1)`, discards its return, and restores ambient `r7` into
`r0`. `verify_boot_ambient_wrappers.py` compares all fixed instruction bytes
outside relocatable BL. `verify_boot_ambient_wrapper_registers.py` executes
stock/source wrappers with controlled child cuts and compares call arguments,
`r0`, `r1`, and SP; both pass.

Native SPOT transition 0x42a43a preserves the original third argument's high
24 bits in a stack selector word, changes only its low byte, then returns that
word in `r0` and original fourth argument in `r1`. Selected C now expresses
that `uint64_t` ABI. The bounded stock/source oracle passes ascending,
descending, and equal-state cases with controlled sequence/callback lowers.

Native 0x4225d0 is now source-owned `memchr` C. The byte-result oracle passes
112 cases over valid mapped inputs. The stock accelerated implementation's
read/fault envelope is not proven equal for inaccessible adjacent memory.

The ADC profile's native 0x42ea6e performs a read at `context+4` before its
NULL comparison. The selected C retained that actual precondition after a
temporary, incorrect guard change was reverted. A focused stock/source oracle
confirms both fault on NULL. A broader ADC runtime oracle cannot execute the
M55-linked source image under current Unicorn CPU support; this does not
establish full ADC behavior equality.

Current selected archive receipt `boot-memchr-spot-return-round/inventory.json`:
350 units, 974 providers, six genuine unresolved imports, target compile and
archive pass. `boot-body-crosswalk-memchr-round.json` has 197 of 903 catalogue
entries without a machine binding. Most of this count is attribution work,
not established missing C. Full firmware still requires code/data/root extent,
linker placement, ROM/hardware contracts, and production/native runtime proof.
