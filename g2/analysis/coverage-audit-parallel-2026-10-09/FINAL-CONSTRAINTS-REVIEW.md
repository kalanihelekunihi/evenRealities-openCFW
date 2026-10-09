# Review of strengthened source constraints

[FINAL-CONSTRAINTS-VERIFICATION.json](FINAL-CONSTRAINTS-VERIFICATION.json) independently checks all seven codec target segments, six VAD callsite byte sequences and three consumed-disassembly hashes. No mismatches were found. PLL table independently decodes to signed `{0,10,15,-10,-15}`.

The pinned SRAM disassembly supplies a 20-byte copy from table `0x10025CE0`, indexed access, increment and compare against five. This supports a five-offset selected target sequence and contradicts unmodified AIoT's three-offset source for that sequence. KWS-like code is supported; exact KWS pin, complete producing checkout and compiler release are not. A separately linked object, private patch or common predecessor remain legitimate alternatives. Source citation refinement: currently registered KWS table is at clock_board.c line 118; AIoT table is line 137. The report's KWS line 137 citation is inaccurate for this working tree, though the values agree.

All six string-load/BSR instruction byte checks agree with authenticated payload. Existing decoder loads the three diagnostic addresses and calls `0x10206C24`, whose printf name is inferred. This is stronger than raw string retention: target code contains diagnostic-address callsites. It does not establish live entry-point reachability, exact callee behavior, surrounding full CFG or runtime execution. An unused linked archive member can retain these instructions as well as its strings. FINAL-CONSTRAINTS explicitly preserves these limits; no unsupported live-reachability or exact-source claim is necessary to accept its bounded statement.

The callback's `andi r0,r0,4`, address `r1+8` and VAD-query target align with LOGFBANK source present in both KWS and AIoT. The `cmplti ...25` after increment aligns with delayed-VAD threshold 25. This is local branch/value compatibility, not proof of original Kconfig macro names or complete configuration. FFT-source removals do not discriminate this shared selected branch. These qualifications are correctly stated in FINAL-CONSTRAINTS.

Board structure/alias and external ARC startup uncertainties remain open. Architecture analogy does not override existing SDK/QK attribution. The local constraints do not add source-complete bytes or establish a byte-identical build.

Only static repository reads and additive audit output were used. No downloaded code, compiler, emulator, Docker execution, canonical edits or denied-path access occurred.
