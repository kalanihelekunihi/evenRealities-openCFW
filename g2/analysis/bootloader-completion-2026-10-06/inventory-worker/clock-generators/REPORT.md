# Clock generation: bounded source recovery

Continuation: [native math validation](MATH-VALIDATION.md) now records4311 native math comparisons and48 CortexM33 native configuration-caller comparisons, plus688 bounded generator cases, on candidatef3ca176e. The floating descendants described as unresolved below have since been implemented and directly tested. All seven integration cases and affected regressions now PASS, frozen hashes/copies reconcile, and f3ca176e is the promoted verified offline checkpoint. Earlier evidence and limits below are retained.

New independent source: `g2/components/bootloader/initializer_callbacks/clock_generators.c` and explicit 12-byte interface in `clock_generators.h`. Direct verification PASS, **688 cases**: HF2 160, PLL selection 48, minimum-VCO 480. This source is **not integrated** into the e1049dc3 checkpoint. No shared campaign, source-image linker, staged files or existing copy controls changed.

## Provenance and source correspondence

Locked bootloader SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, loaded at `0x410000`, little-endian Thumb/VFP. Original functions: HF2 `0x426c24..0x426c4e` (42 bytes); minimum-VCO `0x427040..0x42714c` (268 bytes, adjacent literal pool excluded); selector `0x427160..0x4272ac` (332 bytes). Original-instruction traces are in `comparison.json`; code addresses and instruction bytes are preserved.

Corroborating [public Ambiq Apollo510 source](https://github.com/AmbiqMicro/ambiqhal_ambiq/blob/5efc0228528a8adce5eae0d226fac85d2551eb3b/mcu/apollo510/hal/mcu/am_hal_syspll.c) is saved intact as `am_hal_syspll.reference.c`, SHA-256 `b2ac1b4a89ff7c2e17f57f199998688e9de4a67ca9035d5dbf8063b94da18b28`. It retains its BSD-3-Clause notice and identifies `release_sdk5p1p0-366b80e084`; this is corroboration, not proof of the producing SDK commit/compiler. New implementation was independently written from stock disassembly, not copied vendor implementation.

Stock literals at `0x427594/0x427598` are 60000000/240000000. Table pointer `0x42758c` addresses the 50-byte divider table at `0x431e70`; `0x42759c/0x4275a0` address score B/A at `0x433cc8/0x433cb8`. Public names and frequency calculations establish Hz inputs and MHz conversion here, rather than merely inferring units from constant magnitudes.

## Recovered contracts

HF2 takes `(reference_Hz, target_Hz, shift, out_word)`. It computes integer `reference / (1 << shift)` **before** float conversion, divides float(target) by float(that integer), then uses native VFP unsigned fixed-point conversion with **15 fractional bits**. It stores the word and returns zero. Inline instructions retain architectural shift/UDIV/FP saturation behavior; no undefined C NaN-to-unsigned cast. Null output is not checked. Callers select shift2 by default. Tests include zero inputs, shifts31/32/255/256 and maximum unsigned inputs under the specified emulator FP state.

PLL descriptor is 12 bytes: byte0 caller-selected reference; byte1 VCO mode; byte2 fraction/integer mode (0=fraction); byte3 reference divider; bytes4/5 post-dividers; halfword6 feedback integer; word8 feedback fraction. Ordinary SDK enum layout cannot be substituted for the explicit stock small-enum ABI.

Minimum-VCO helper first calls GCD in MHz. GCD<1 raises the minimum to `10 * (reference / (reference / 10000000))` if larger. It rounds minimum/target up, rejects divider>=50, and chooses the table's achievable post-divider pair. Multiplication uses uint32 wrap. VCO generation receives float(reference)/1e6 and float(target*actual_divider)/1e6. After child success it computes rounded-up PFD; minimum is10MHz for fraction mode0, otherwise1MHz. Low PFD returns5 without undoing the child writes; only accepted PFD writes post1/post2. This failure-partial-write behavior is relevant when reusing an output descriptor.

Outer selector tries both minima, accepts child status0, and computes uint32 scores:

`score = ((reference/1000000)*B[index])/refdiv + ((target*post1*post2)/1000000)*A[index]`

`index = (fraction_mode==0) + 2*(vco==1)`; A={435700,465700,131525,139025}, B={228000,396000,228000,396000}. The cheaper successful candidate wins; **ties select the second**. No successful candidate returns5 and leaves caller output unchanged. Success copies offsets1..11 and preserves byte0. It does not validate the destination pointer. No allocation, retained pointer, queue or hardware writes occur in these outer bodies.

## Validation and limits

The runner executes original bytes and compiled reconstruction under Unicorn A15, with FPSCR initially0, comparing return, destination, child arguments and final FPSCR. HF2 has no child stubs. Selection tests cut minimum-VCO identically in both machines. Minimum-VCO tests cut **GCD `0x426d48` and VCO generation `0x426f6c`**, supplying explicit synthetic results/layouts. These cuts are not a claim that all synthetic descriptors are physically realizable. No SRAM write hook is installed; prior copy-hook reproductions remain untouched.

`negative-control.log` preserves a rejected candidate changing fixed-point scale15 to14: first meaningful nonzero comparison produces `0x0bb80000` vs `0x05dc0000`. The bad candidate was compiled only under `/tmp`; production source and verified ELF were not changed. No integration suite, live scheduling, physical PLL lock, alternative FPSCR mode, hardware timing or byte equality is certified.

Run `make verify` here for the bounded direct suite; it uses `/tmp` build outputs. The saved receipt records exact candidate/source/runner hashes. Dependencies still requiring native recovery/validation are the floating GCD and VCO generator with their floor/ceil/round and integer/fraction helpers. They are actual source-closure work, not missing external hardware inputs. Do not replace the e1049dc3 generator aliases until those bindings and candidate-specific integration tests are ready. Heavy seven-case work remains deferred during the coordinated ingestion window.
