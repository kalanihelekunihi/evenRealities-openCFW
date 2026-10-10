# Complete authentic DSP C alternative: compile/link proof

**PASS: ten authentic C translation units compile and link into a C-SKY ELF with no undefined symbols.** All six references from the earlier wrapper-only experiment are resolved, including radix4 butterfly/inverse, split real/inverse, csky_cfft_q15 and csky_bitreversal_q15. The complete dependency closure also includes radix4-by2 forward/inverse and bitreversal_16. ELF SHA256 d86634e6c9a11b2f8bb8f3fb5468340d89c547a229ebbb6ae1bd8028c93a572a. This is a standalone function-library link proof, not bootable firmware, an integrated image or numerical/byte equality.

## Additive correction

The predecessor's missing-kernel-source claim was incorrect. Authentic C definitions already exist in the registered NationalChip SDK: csky_radix4_butterfly_q15.c and csky_split_rfft_q15.c. Earlier undefined references showed omitted translation units, not absent definitions. Discovery's kernel-lineage report establishes the separate files and Makefile's deliberate assembly selection. Its public import a47076981e6c1ac3b9b1073c3e3e9466d8de7ea8 already contains that selection. Both older sealed packets remain unchanged; their hashes verify.

## Build evidence

Unchanged sources from pin8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5 retain their Apache-2.0 notices. Compile recipe remains GCC6.3.0 B20190929, -mcpu=ck804ef -mhard-float -O2 -g -fno-builtin -fstrict-volatile-bitfields -ffunction-sections -fdata-sections with SDK-declared include paths. Ten linked units: CFFT radix4 wrapper, RFFT wrapper, radix4 butterfly pair, split pair, bitreversal, CFFT dispatcher, radix4by2 pair, shift, copy, fill. No source edits, assembler objects or archived executable blobs were linked.

The first nine-unit link failure is retained in build-results.json. It identified the existing radix4by2 unit and missing bitreversal_16. Generic C bitreversal_16 is guarded by FOR_X86_64 in the authentic source; only that translation unit was recompiled with -DFOR_X86_64=1 to expose its existing pure C definitions while targeting C-SKY. This is an explicit alternative configuration, not a claimed stock or host-architecture build. No arbitrary optimization/SIMD/endian flag sweep occurred. All other units retain the fixed recipe. link-completion-results.json contains commands, hashes, complete resolved-symbol addresses and empty undefined list; complete-c.map provides link placement. Entry symbol csky_rfft_q15 and illustrative text placement10003000 do not make a runnable boot image.

Prior assembly result still proves nine exact sections/1606bytes with17 independent checks. Current C output differs where previously compared; stock Makefile intentionally selects assembly. This experiment establishes that the authentic C alternative is compilable/linkable, not that it should reproduce assembly bytes.

## Numerical execution boundary

No numerical vectors were executed. Installed Unicorn exposes no C-SKY backend. Existing chosen amd64 container has neither qemu-csky nor qemu-system-csky. Archived C-SKY GDB fails before target-sim probing because libncurses.so.5 is absent (existing libraries are ncursesw6/tinfo6); simulator support is therefore unverified. No package installation, ABI-substitute symlink, host-C surrogate or hand-written instruction model was introduced. A working compatible C-SKY instruction simulator supporting these CK804 DSP instructions plus defined ABI/memory fixtures is the exact next prerequisite for authentic assembly-versus-C Q15 numerical comparison. Passing host-C tests would not close that boundary.

No production/canonical/Pigweed/Git/device changes. Source/link/numerical/byte-equality evidence remain distinct. No whole-firmware completion, runtime alias, source percentage or coverage admission is claimed.
