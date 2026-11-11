# Native recurrent support in C

`native_model_recurrent_support.c/.h` implements four native ABI entries:
round`0x290dc`, zero-point`0x6fde0`, unsigned-byte matrix`0x7405c` and range
adjustment`0x36408`. These dependencies prepare the recurrent callback.

Round0x290dc and zero-point0x6fde0 delegate to actual C quantize-round/index providers for separately rounded bias-first half-away rounding, signed RTZ/saturation/status, maximum(1e-4,width),255/width and offset*inverse. Native instruction ordering and all32 FP configurations confirm these shared operation contracts. No algorithm models or native fallbacks execute.

Matrix0x7405c ignores fourth register argument; four stack arguments are signed-traversal columns/rows and two32-bit zero points. Read unsigned input/weight bytes live, subtract zero points modulo32, multiply and sum modulo32, then store a row result. Earlier stores can alter later input/weight reads. Negative counts and native four-element grouping reduce to the same tested data effects. Scalar R0 returns original input pointer; native incidental R1-R3 restoration is outside the C scalar contract.

Range0x36408 caches both endpoint bits, subtracts high-low, and admits carry&&!zero from signaling compare, including unordered. Equal-zero lower exits without changes. Point=(-255*lower)/width, actual C floorf, and signed raw-bit fraction thresholds determine adjustment eligibility. Fraction>=.5 selects floor+1; policy is low two bits.

Policy0 uses GE for comparison of (fraction-1)*low and fraction*high; policy1 uses a scaled GT branch; policy2 uses carry-clear after the other scaled comparison; policy3 applies a separately rounded bounded translation. Point/floor thresholds are signed raw bits, not numeric float comparisons. Selected upper adjustment changes only high; lower adjustment only low; translation writes low then high. Returns are ffffffff,0,1,2,3 and full FPSCR is preserved/updated as native.

REA complete function-manager dossiers/pseudocode/assembly and authenticated raw bodies cover all660 bytes. Range literal pool authenticated. Actual C shared headers preserve the entire tested candidate object byte-for-byte. No new assembly or writable global state is introduced.

321,024 stock/C comparisons pass:294,336 direct and26,688 with normal objects.
Tests exercise all32 FP configurations, all five range return codes, signed
matrix counts, zero-point wrap and live overlaps. All660 bytes/204 instruction
starts execute. Sixteen compiled defects are rejected: round result, zero-point
bounds, signed bytes, either zero point, matrix row stride/result/count sign,
ordered width guard, numeric fraction gate, policy mask, selected ceil, upper
divisor, translation constant, lower denominator and upper store target.

All931 normal units compile without failures or duplicate strong symbols.
All920 prior nongenerated source/object pairs are unchanged. Normal sections and
decoded symbols match tested candidate after source-file metadata normalization.
Imports stay69 application/22 boot. Source plan and cache layout are unchanged.

Valid mapped input/weight/output spans and aligned word results/endpoints are required. Tests cover negative/zero signed counts, zero-point wrap and six live aliases; they do not assign fallback behavior to invalid huge matrices.

Public RAM/full FPSCR, saved R4-R11/S16-S31, SP/masks and scalar R0 are checked.8192 private bytes below incoming SP and caller scratch/APSR are excluded. All660 bytes/204 instruction starts execute, not all inputs or interleavings. Timing, interrupts, concurrency and cold FPU are outside proof.

Independent finite arithmetic, zero-point endpoints, modular dot products and range policy/grid checks pass. Grid-point tolerance1e-4 and endpoint tolerance1e-6 belong only to those independent finite oracles; direct native/C comparisons remain exact.

Probe linker enum-size warnings retained; called interfaces use pointers/integers/floats rather than enums. Normal931-unit relocatable composition remains69 application/22 boot imports. Recurrent and quantized convolution callbacks, parent SpO2 stages, other hardware dependencies, startup and physical boot remain unresolved/unverified.

[Machine-readable evidence](goodix-recurrent-support-c-review.json).
