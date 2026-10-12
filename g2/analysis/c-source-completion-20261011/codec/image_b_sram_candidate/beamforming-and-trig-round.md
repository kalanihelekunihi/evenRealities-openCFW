# Image-B beamforming and binary64 trigonometry round

The separate CK804EF hard-float candidate is built by `build.py` with
`--output build-create-overlap-round --reuse-receipt build-create-temp-round/receipt.json`.
The latest hash-coherent receipt contains 192 C/assembly source units and a
relocatable object SHA-256
`67d5adea8ec154bec04fac7e86a8c6f78520c5a9b462e76a33860d343462e120`.
Its eleven remaining undefined symbols are the five genuine DSP/body or FE
contracts (`beamforming_angles`, `beamforming_core`, `beamforming_process_core`,
`__fe_getround`, `__fe_raise_inexact`) and six genuine BSS, initialized data,
native-zero-word, or ambient-direction contracts. See the receipt for exact
symbol spellings.

`backup_beamforming_create_wrapper.c` expresses the authenticated native
0x1000de40 argument remap. `backup_beamforming_process_wrapper.c` expresses
0x1000dea0 and its target object reproduces the native 20-byte instruction
sequence modulo the lower-call relocation. The beamforming initializer at
0x1000b800 is source-backed by the pinned NationalChip SDK, but the vendor GSC
implementation itself is absent from that pinned tree. Native angle 0x1000c6e8
has discontiguous Ghidra ranges and FPU bad-data edges. Native process core
0x1000d46c is catalogued as only 140 bytes, while authenticated disassembly
continues after 0x1000d4f8 through branches reaching at least 0x1000dd9c.
Neither Ghidra envelope nor truncated pseudocode qualifies a full core body.
The separate `backup_beamforming_angle_entry.c` now expresses native
`0x1000c6e8..0x1000c744`: count check, exact diagnostic string and -1 return,
signed degree-to-radian conversion with native binary32 π bits, and ready flag.
It deliberately has a distinct helper symbol and does not satisfy the full
`0x1000c6e8` import. Host checks pass the mismatch and zero-count paths;
positive-count memory effects follow the decoded halfword loop and compile for
CK804EF but have no C-SKY runtime comparison yet. Downstream trigonometric
paths remain to be reconstructed before full-angle registration.
The native zero-mode `0x1000c868..0x1000c8a4` spacing loop is also source
expressed in `backup_beamforming_angle_spacing.c`, including the unconditional
first two vector writes, float division by mic count, and scaled distance.
Host output fixtures for 2, 3, 4, and 8 microphones pass. This is a separate
body slice pending composition with angle geometry and later matrix updates.
The zero-mode sine matrix at native `0x1000c8ae..0x1000c90c` is expressed as
an angle-major loop that subtracts each microphone position and calls the
source-owned vector sin adapter. A host callback fixture confirmed the
angle/microphone write order for 3×2 positions. The nonzero-mode branch at
`0x1000c83e..0x1000c85e` copies the radian angle vector and invokes the same
sin adapter for the positive-count path. These two branches are separate
compiled chunks, not yet a full provider or stock runtime proof.
The subsequent inner phase vector slice at native `0x1000c970..0x1000c9b2`
is also C: it scales a matrix row by `float(frame_index) * fr8` and invokes
source-owned vector sin followed by vector cos. A host callback fixture
confirmed scaling and output array order; exact native float-register and
exception behavior still needs target execution qualification.
An earlier two-microphone multiplier in this slice was corrected after native
stack-slot lifetime analysis: `0x1000c936` resets slot `0x0c` to frame zero,
and `0x1000ca58` increments it once per complete angle sweep. The composed
zero-mode phase table now traverses those frame and angle dimensions and
combines the vector and reciprocal-normalization chunks. A host fixture
confirmed frame-zero identity coefficients and two-angle slot placement.
The phase-normalization path at `0x1000c9e0` uses C-SKY `frecips`. A separate
source-owned assembly leaf `backup_beamforming_reciprocal.S` now expresses the
named instruction with fr0 input/output. Target disassembly is
`f4000320 frecips fr0, fr0; 783c jmp r15`, and a compiled CK804EF caller
passes the float through fr0 without register moves. The native body uses the
same instruction on fr2 (`f4020322`); C composition can call this leaf without
replacing it with `1.0f/x`. Approximation and FP exception effects still need
native execution qualification.
The complex normalization body `0x1000c9be..0x1000ca38` is now another C
slice. It writes `(1,0)`, computes the first sine/cosine magnitude, calls the
native reciprocal leaf, and writes subsequent real/imaginary pairs. The target
compiler emitted `fmacs` and `fmscs` for the two fused expressions, matching
the authenticated native instruction classes. A host fixture checked the
coefficient layout for three unit phases; that fixture substituted ordinary
reciprocal only to verify array layout, not the CK804EF approximation.
The alternate native angle sweep `0x1000ca88..0x1000cade` is source-expressed
as angle-major `float(index)*steering - microphone_position` generation and
vector sin calls. This is compiled but remains a slice of the full CFG.
The fallback `0x1000cae0..0x1000cb10` now has C for its unconditional zero
write, iterated binary32 steering-angle addition, and vector sin call.
The table update `0x1000cb1e..0x1000cbd2` is now C as a frame × angle ×
microphone traversal: it generates a phase from frame index and the saved
frequency increment, calls vector sin and cos, and writes interleaved output
to the context table. A host callback fixture confirmed a 2-frame, 2-angle,
2-microphone slot layout. The separate
`gx8002_image_b_beamforming_angles_whole_candidate` composes the decoded
entry, allocations, geometry, mode branches, tables, and native six-buffer
cleanup. It intentionally has a distinct symbol: the true `0x1000c6e8`
provider stays imported until executable native/C state comparison qualifies
both mode branches and edge effects. The product allocator/free callback table
at `0x2002d7a4` remains a typed link contract; no default was supplied.
The create core has begun with `backup_beamforming_create_prefix.c`, native
`0x1000ce14..0x1000cf04`: 220-byte context allocation, exact scalar/FPR
field pattern, 400-byte and `angle_count*4` allocations, and the XOR-mode
diagnostic with exact stock string from `0x10014158`. A host fixture verified
the 220/400/12 allocation sequence and thirteen selected context fields for
the product call. This prefix has a distinct symbol; the complete create core
at `0x1000ce14` remains a genuine import.
The next native create span `0x1000cf04..0x1000cfae` is source-expressed as
thirteen further allocator calls with exact context fields and unsigned
32-bit size arithmetic. A host fixture passed all thirteen call sizes for
the product dimensions (2 microphones, 3 angles, one output), including the
12,336-byte phase table and 6,168-byte cross-microphone table. No early
allocation-result policy was invented.
Create angle defaults at `0x1000cfb0..0x1000cfd8` and
`0x1000d19c..0x1000d1e0` are now C for linear and circular branches. They
retain the native integer division behavior, stock `0x40875c29` angle word,
and circular `0x3f8ccccd` binary32 scale; circular count zero remains an
actual divide-by-zero path rather than a guessed value. The buffer
initialization at `0x1000cfd8..0x1000d03c` now calls the source-owned native
zero writer four times, seeds the `angle_count*257` table with stock
`0x47c35000` words, and copies the requested output-index bytes. Target
archive compilation passes; positive-count host memory effects need a
32-bit-address harness or target emulation because these context fields are
native 32-bit pointers.
The 512-element create window `0x1000d03c..0x1000d09e` now has C with
the stock `2π`, `0.46`, `0.54`, and `32768` binary32 words. Target disassembly
reproduces the native `fsitos`, `fdivs`, `fmuls`, `fnmacs`, and `fstosi.rz`
sequence in the loop, modulo register allocation and the source-owned sin
call relocation. This is stronger instruction evidence for the body than a
host window-value comparison; physical FP exception behavior remains open.
The create temporary allocation at `0x1000d0a0..0x1000d0ca`, with its
`0x1000d1e2` failure diagnostic, is also C. Product dimensions request
6,144 bytes. A host fixture checked the exact request, full zeroing via the
source-owned zero writer, and null return/log path.
The create tail `0x1000d0ce..0x1000d160` now has a C overlap-add loop and
inverse window normalization over the temporary buffer, followed by the
native release callback. A host fixture checked five shifted overlaps,
central six inverse entries, and release order on a small frame. Target
disassembly confirms native integer multiply/asri15 and
`fdivs/fmuls/fstosi.rz` instruction classes. Product-memory execution and
path-complete native/C comparison remain necessary before binding
`0x1000ce14`.
`backup_beamforming_create_whole_candidate.c` now composes the native create
prefix, all later allocations, angle defaults, buffer preparation, window
generation, temporary allocation/failure diagnostic, overlap-add, inverse
normalization, and temporary release. The 32-bit product allocator/free table
remains a typed external contract. This is deliberately a distinct experimental
symbol; the genuine `0x1000ce14` symbol remains undefined until end-to-end
native/C memory and FPR effects on target product state are proven. Coherent
CK804EF build: 193 units, linked-object SHA-256
`bb74f666027b7b5a7f19ec21d449a0e4aa4fa4ad6b092c3efb96435f3504021e`,
receipt `build-create-whole-round/receipt.json`. Eleven genuine imports remain.
The next process-core slice `backup_beamforming_process_dimensions.c` translates
native `0x1000d47e..0x1000d4e6` into the frame-local microphone, stage,
frame, angle, and scratch dimensions with explicit 32-bit wraparound. Each
field has a source context offset and native stack offset in the C type.
This does not include the branch-heavy FFT/matrix calculation or define
`0x1000d46c`. The new coherent build has 194 units, linked-object SHA-256
`7e92863e446a8849ca310d31ff9435181467a5330aff46bce179c8f224e61cf1`,
receipt `build-process-dimensions-round/receipt.json`, with the same eleven
true imports.
The process band's native `0x1000d4ec..0x1000d548` plus out-of-line
`0x1000dd80..0x1000ddd4` comparator branches are now C in
`backup_beamforming_process_band.c`. A target GCC comparison probe confirms
`fcmphss fr1,fr0` is `alpha <= threshold` and `fcmplts fr1,fr0` is
`alpha > threshold`; the code retains the native unordered/NaN route to
existing product fields at context +0x4c and +0x50. A host fixture passed
nine exact binary32 threshold and NaN cases. This is a bounded source slice,
not the complete FFT/matrix process provider. Coherent build: 195 units,
linked-object SHA-256
`521a3d46e72350933a6c440e2ab476deb3b99ad7b240c04afe13d9e9cf1024a8`,
receipt `build-process-band-round/receipt.json`, eleven genuine imports.
An independent Linux AArch64 `-no-pie` host fixture maps every allocation at
a distinct address below 4 GiB, so the source's native 32-bit context pointer
fields are exercised without pointer truncation. The full create composition
passes the product positive path: all 17 allocation sizes and their order,
context dimensions, three angle defaults, copied output index, temporary
release, and final context pointer. This establishes source composition and
32-bit memory-field behavior under host `sinf`; it is not an original C-SKY
execution comparison, binary32 exception check, or failure-path proof.
The same low-address fixture then calls the composed angle candidate on the
created product context. The linear-mode positive path passes six temporary
allocation sizes and release order, three degree-to-radian writes, ready flag,
and first complex-table slot for two microphones. A second mismatched-count
call returns `-1`, clears ready, emits the authenticated diagnostic exactly
once, and makes no allocations. The fixture uses host sin/cos and reciprocal
stubs, so this is a 32-bit pointer/layout and call-flow check, not target
numerical or native whole-body equivalence. The true `0x1000c6e8` import
remains open.
`backup_beamforming_process_prepare.c` covers the subsequent native
`0x1000d548..0x1000d5bc` clear and ring-row setup. The observed product
counter word at `0x2002d7a0` is a typed caller input; no initial value is
fabricated. It preserves native division/remainder by context +0x48,
threshold/coefficient pointer offsets, the source-owned halfword DSP clear,
and the conditional row clear. The low-address host fixture passed both
four-halfword scratch clear and the selected three-halfword ring row for a
counter of seven. Coherent target build: 196 units, linked SHA-256
`5580d573e3881198d8541083fbd0645c9190317f1b9fcece230ad9b9a2033ef2`,
receipt `build-process-prepare-round/receipt.json`, eleven genuine imports.
The complete matrix/FFT process body remains open.
The complete shared arithmetic leaf `0x1000e1e8..0x1000e238` is now source
in `backup_beamforming_complex_ratio.c`. It computes the two binary32
quotients of a complex pair, preserving the native first multiply followed
by fused add/subtract and a separately evaluated squared denominator for
each output. Initial use of `__builtin_fmaf` emitted an external `fmaf`
call, so the final C uses explicit volatile intermediate products. CK804EF
disassembly now shows the native `fmuls`, `fmacs`/`fmscs`, `fdivs`, and two
stores in matching arithmetic order; a host fixture passes two concrete
complex quotients. The native leaf's FP exception behavior and full process
caller remain unqualified. Coherent target build: 197 units, SHA-256
`e72d4573d99164e791af9e44ed64310e21481a55d07e267e8ba5d42daecbd245`,
receipt `build-complex-ratio-v5-round/receipt.json`, eleven genuine imports.
The adjacent complete leaf `0x1000e23c..0x1000e288` is now
`backup_beamforming_complex_negative_ratio.c`: it negates the same two
quotients using the native `frecips` child. A focused CK804EF comparison probe
established `fnmscs` as the negative fused sum and `fnmuls` as negative
multiplication; the compiled source emits those native instructions in the
same arithmetic sequence, modulo a call to the existing reciprocal leaf.
The host fixture checks both signs on a concrete complex input. Coherent
target build: 198 units, linked SHA-256
`5268982ba67b17829c29b3836d312e2a6b5e823dac154dc50ca1b03bde5e3e8a`,
receipt `build-negative-ratio-round/receipt.json`, eleven genuine imports.
The next complete GSC matrix leaf `0x1000e0b8..0x1000e144` is now
`backup_beamforming_complex_matrix.c`. It consumes the native fifth stack
argument for row count and walks the second operand in column-major complex
rows. It preserves each intermediate output store, including zero-column
and zero-row behavior. CK804EF disassembly shows the same fifth stack load,
row/column strides, `fmuls` plus `fmacs`/`fmscs`/`fadds`, and two output
stores per inner iteration, with only local temporary stores added by C.
A two-by-two host fixture passes exact small-integer outputs and empty-axis
cases. Coherent target build: 199 units, linked SHA-256
`11b1047ce6bc209f67522ec5e8203d2b7ad867550f88a6883ffa96bb419c66ce`,
receipt `build-complex-matrix-round/receipt.json`, eleven genuine imports.
The second complete matrix leaf `0x1000e148..0x1000e1e4` is
`backup_beamforming_complex_rows.c`. Its live process caller at
`0x1000d82c` authenticates the two consumed stack arguments: complex column
count and output row count. The vector is reused for each row; the matrix
advances contiguously through each row. CK804EF disassembly confirms the
adjusted stack-slot loads after the C frame, intermediate output stores,
ordered `fmuls/fmacs/fmscs/fadds`, and row strides. A two-by-two and empty-axis
host fixture passes. Coherent target build: 200 units, linked SHA-256
`95e658a2bda337418ace9b6b1c62cb01fd735e32619510f592e51bbaa0359588`,
receipt `build-complex-rows-round/receipt.json`, eleven genuine imports.
The connected GSC energy helper's native prefix `0x1000cc82..0x1000ccfc`
is C in `backup_beamforming_energy_prefix.c`: signed 16-bit complex sample
squares with 32-bit wrap, frame-indexed energy output, and the first-use
product flag at `0x2002d79c` that initializes scaled energy and baseline
arrays. Its remaining `0x1000ccfc..0x1000ce02` adaptation loop is still
missing, so the full helper symbol is not defined. A low-address host fixture
checks normal and overflow energy, scaled values, baseline 127, first-use
transition, and later-call preservation. Coherent target build: 201 units,
linked SHA-256
`6583acb9d67a56b6ad2fb682c410e56325c0c86464ad2f730681f7cd9d7b00a5`,
receipt `build-energy-prefix-round/receipt.json`, eleven genuine imports.
The mode-enabled energy smoothing loop `0x1000ccfc..0x1000cd36` is now
`backup_beamforming_energy_smoothing.c`, retaining both signed arithmetic
shifts, the two 32-bit coefficient products (107 and 19), and frame-indexed
in-place writes. The low-address fixture checks bypass at mode zero and two
positive adaptive values at mode one. The following floating gain/log loop
still belongs to the unimplemented remainder of `0x1000cc70`. Coherent
target build: 202 units, linked SHA-256
`fd9e2f65d0510f1e0e2a04a586635ab59c9514b8bba0a2435b26eea3a80e7544`,
receipt `build-energy-smoothing-round/receipt.json`, eleven genuine imports.
The non-diagnostic numeric gain path at `0x1000cd50..0x1000cdae` is now
`backup_beamforming_energy_gain_numeric.c`. Target disassembly emits the
native signed division, `fadds/fdivs/fmuls/fstosi.rz`, max-9830, Q15 shifts,
and sample stores with the authenticated binary32 constants. A low-address
fixture checks baseline update, gain floor, and positive/negative Q15 sample
rounding. The native negative-baseline diagnostic at
`0x1000cdc0..0x1000cddc` and exceptional conversion/FP behavior remain
outside this slice. Coherent target build: 203 units, linked SHA-256
`01685f5fc2547c07d8882ff49875212244e792dda2700fb00bf043098ab8ec04`,
receipt `build-energy-gain-round/receipt.json`, eleven genuine imports.
The next separate helper, `backup_beamforming_angle_allocations.c`, expresses
native `0x1000c746..0x1000c7ea` plus the allocation failure diagnostic at
`0x1000cc34`: context scalar loads, frame ratio, all six allocator calls in
native order with sizes `angles*4`, `mics*4` three times, `mics*angles*4`, and
`angles*4`. It checks every returned pointer only after the sixth call, exactly
as native does. A host fixture passed the six-size/order check and null results
at first, fourth, and last positions. The diagnostic text and file name were
read from authenticated native initialized data at `0x10014270/0x10014254`.
This helper also remains distinct from the full angle symbol.
`backup_beamforming_angle_geometry.c` expresses native `0x1000c7ee..0x1000c834`:
source-owned `sin` adapter call, binary32 constants `2π`, `π`, `340`, and
`180`, the frame ratio and steering conversion, and the conditional negative
product on the nonzero mode path. It compiles into the CK804EF archive; exact
native numerical execution and downstream matrix population remain open.

Direct native instruction review shows the three full control-flow regions:

| Entry | Native instruction lines before next public entry | Direct called children | Observed frame-pop sites |
| --- | ---: | --- | --- |
| `0x1000c6e8` angle | 633 through `0x1000ce12` | diagnostic `0x10009934`, sin adapters `0x1000ded0/0x1000dee0`, cos adapter `0x1000df0c`, runtime `0x10011af4` | `0x1000cc1a`, `0x1000cdf0` |
| `0x1000ce14` create core | 567 through `0x1000d46a` | diagnostic, trig, `0x1000ef64/0x1000f0c0/0x1000f134/0x1000f1ac`, memset `0x100113c4` | `0x1000d176`, `0x1000d29c`, `0x1000d3ee` |
| `0x1000d46c` process core | 857 through `0x1000de3e` | DSP children at `0x1000cc70/0x1000df38/0x1000e004/0x1000e0b8/0x1000e148/0x1000e1e8/0x1000e23c` plus copy/FFT helpers | `0x1000dd44` |

The complete source requirement is therefore these three large CFGs and their
seven process-core internal DSP children. Five of those child addresses have
no separate decompiler function file; they are branches into shared native
regions. Native instruction provenance is present, but a checked C translation
and true frame/float-register ABI mapping are still required. The process-core
one-frame return at `0x1000dd44` is an executable body boundary, unlike the
catalogue's `0x1000d4f7` suffix. These counts describe disassembly lines,
not proven independent C function counts.

The image-B sin/cos chain now has source bodies for entry functions, kernels,
argument reduction, kernel argument reduction, fabs, floor, and scalbn. The
Sun fdlibm originals are pinned under
`third-party/upstream/android-bionic-fdlibm-a27d2baa/libm/src/` at commit
`a27d2baa0c1a2ec70f47ea9199b1dd6762c8a349`. Included source hashes for
`e_rem_pio2.c` and `k_rem_pio2.c` are recorded by the builder. The floor/scalbn
source is a little-endian word-macro expansion of pinned `s_floor.c` and
`s_scalbn.c`. A host bitwise check compared 9,998 non-NaN random patterns for
each helper with host libm and passed; this is not stock C-SKY runtime or
exception-flag equivalence. A separate host check compared 5,000 input pairs
each for the kernel sin and cos bodies with pinned original C and passed
bitwise. Full target hardware and FP environment proof remains open.

Image-B still lacks complete native body coverage, initialized product data,
final loaded-image scatter/entry placement, compact IRQ assembly, and hardware
qualification. Relocatable link closure is a narrower milestone.

The current address-suffix census finds 254 of 288 catalogue entry strings in
candidate C and 34 outside. This is a triage index only: the three GSC core
entries are counted because typed external declarations mention them, although
their bodies are absent. The 34 outside also contain resident compiler-runtime
aliases, formatter functions owned by the pinned selected printf source, and
data boundaries. Neither count represents qualified whole-body completion.

## Energy helper and process threshold continuation

`backup_beamforming_energy_whole_candidate.c` composes native
`0x1000cc70..0x1000ce02` from previously checked prefix, smoothing and gain
slices. Its negative-baseline branch logs the low and high words of the
finite binary32-to-binary64 widening performed by native `0x10011af4`, before
the corresponding gain update. The exact stock format at `0x100141ec` is
`[error]:%d, %d,\n`. The low-address fixture checks diagnostic words for
`-116.0`, first-use behavior and affected baseline. This is a separate
experimental symbol; the full GSC process does not yet call it. Exceptional
FPU state and product first-use word initialization remain open.

`backup_beamforming_process_thresholds.c` source-reduces the native
`0x1000d5bc..0x1000d648` loop: unsigned halfword pairs, ordered complex
division, strict lower and upper imaginary thresholds, and a halfword ring
counter increment. Its host fixture checks inside, equal-bound and empty
range cases. This is a bounded slice; substantial FFT/matrix process control
flow remains untranslated.

The separate loaded image-B CK804EF archive is now 205 source units with 11
true imports, including all three full GSC core entries. Coherent receipt:
`build-process-threshold-round/receipt.json`, linked object SHA-256
`5a88556fa4ca0314c7c7cd4aaad2de5681167afeaa2887b7188998d01b6259f1`.

The next native process transition `0x1000d656..0x1000d6b4` is in
`backup_beamforming_process_ring_average.c`: unsigned ring halfwords across
the native `ctx+0x1c` stride, ordered binary32 accumulation/division, strict
`ctx+0xa8[1]` threshold, stage scratch flag, aggregate scratch increment,
and observed `0x2002d7a0` counter increment. A low-address host fixture
checks below/equal/empty-column branches. The ring counter and threshold are
still source-owned runtime inputs, not invented initial values. Current
coherent CK804EF receipt: `build-process-ring-round/receipt.json`, 206 units,
11 genuine imports, linked SHA-256
`1d5816db7a6ff733494e9ed4903f7f7191052da616dc33796e67b4c6bc18fab2`.
The parent `0x1000d46c` remains unresolved; FFT/matrix and later exit CFG are
still substantial native work.

`backup_beamforming_process_diagonal.c` now reduces process
`0x1000d6b6..0x1000d79a`: the selected row comes from the observed pointer at
`ctx+0x5c`, each destination matrix row starts `(1,0)`, and the next complex
slot receives the existing negative-ratio leaf over adjacent source pairs.
The host fixture caught and then corrected a mistaken expected second pair:
the native coefficient pointer advances one complex pair per bin while the
destination advances a full `(ctx+0x04)+1` complex row. The final fixture
checks both rows. Current C-SKY receipt `build-process-diagonal-round/receipt.json`
has 207 units, 11 genuine imports and linked SHA-256
`5f58340d73636bf813d436f08cd5f2dbc299354ceea87c14b1c232d968fb6945`.

The process call to `0x1000df38` reaches a returning `pop r4-r5` epilogue at
`0x1000e002`. Pinned GCC `gcc/config/csky/csky.md` `*pop_multi` RTL includes
`(return)`, resolving an earlier disassembler-notation misread that suggested
fallthrough into `0x1000e004`. These are independent native entries. Their
whole source bodies are now in `backup_beamforming_complex_matrix_product.c`
and `backup_beamforming_complex_block_dot.c`, each with focused host cases.
The matrix product's fifth and sixth arguments come from actual caller stack
words; the block dot's fifth word is its complex pair count.

`backup_beamforming_process_matrix_stage.c` composes actual `0x1000d7f8` to
`0x1000d8ce` call order: matrix product, row product, matrix transform, then
residual conversion. The selected row and coefficient byte offset remain
caller inputs. A low-address fixture runs all four source providers together
and checks both complex matrix outputs and the final signed halfword pair.
The separate CK804EF archive is now 212 units with 11 genuine imports,
linked SHA-256 `c2e4ca3375a1c8ce13f3dc1ede4536f6ebb56e6c5328057821bf03447d4de25a`
at `build-matrix-stage-round/receipt.json`. Later process `0x1000d8ce`
FFT/energy/exit branches and full-entry state remain unfinished.

`backup_beamforming_process_pack.c` covers native `0x1000d7a0..0x1000d7f8`:
`ctx+0x08` input modes, `ctx+0x18` halfword-stream stride, and interleaved
binary32 destination at `ctx+0x6c`. The caller-supplied band byte offset
preserves the preceding loop's state. Low-address host cases check the exact
first/second-stream interleave and zero-mode no-write branch. Current
CK804EF `build-process-pack-round/receipt.json` has 208 units, 11 true
imports, linked SHA-256
`c0011cb60c38d2dc04db2c445eb5d4a8e06217dcdccc2c5ba76f2114462ca4cf`.

`backup_beamforming_process_residual.c` covers native
`0x1000d852..0x1000d8ce` after the two matrix leaves. It divides complex
matrix output by `ctx+0x04`, subtracts paired reference components, stores
residual binary32 at `ctx+0x68`, then converts toward zero into strided
halfwords at `ctx+0x90` plus the caller's band offset. The low-address fixture
checks two modes, signed truncation and exact stride. CK804EF compiler output
contains native `fdivs`, `fsubs`, and `fstosi.rz`; finite in-range values are
verified, while exceptional conversion/FPU flags remain unqualified.
Current coherent receipt `build-process-residual-round/receipt.json` has 209
units, 11 genuine imports, linked SHA-256
`5397602d8a79b6bf30dc598c5dae8ef98abaf62c00ab6beafe5e9fa6d5270f8a`.

## Stack-lifetime ABI correction and later energy statistic

Direct native stack tracing distinguishes stack+`0x18` from context+`0x18`.
Native d4a0 writes `ctx+0x04 - 1` to stack+`0x18`; d48c writes `ctx+0x18`
to stack+`0x38`; d502 loads `ctx+0x48` into live r6. Consequently the
diagonal pass count is `ctx+0x04 - 1`, the d80c/d846 matrix call dimension is
`ctx+0x48`, and the d930 block-dot count is `ctx+0x04 - 1`. Earlier 207-212
unit receipts used `ctx+0x18 - 1` for two of these and must not be read as
native-equivalent matrix-stage evidence. Corrected source and host fixtures
set `ctx+0x18` and `ctx+0x48` to intentionally different values.

`backup_beamforming_process_energy_stat.c` covers native
`0x1000d8ce..0x1000d926`: the aggregate scratch flag at `ctx+0xb4`, ordered
sum of squared `ctx+0xcc` binary32 components, scale bit pattern
`0x3c23d700`, decay `0x3f7d70a4`, and write to the caller-indexed
`ctx+0xb8` slot. Its low-address fixture passes gated and active paths.
Target disassembly confirms `fmacs` accumulation and weighted update.
Current corrected CK804EF receipt `build-stack-abi-correction-round/receipt.json`
has 213 units, 11 true imports, linked SHA-256
`780a37de921c0ba0594c6910e27c4d4d711e30887721ee22253e554a7e0d5f9b`.
Later d928 block-dot consumption and remaining process exits are still open.

The d928 block-dot call and `0x3c23d70a / energy` scale are now in
`backup_beamforming_process_block_scale.c`, with output blocks from native
stack+0x18 (`ctx+0x04 - 1`), pair count `ctx+0x08`, and caller-supplied
stack scratch. The unrolled `0x1000d94c..0x1000da9c` coefficient updates are
in `backup_beamforming_process_coeff_update.c`; at most fourteen source
coefficients are touched in pair order. `backup_beamforming_process_adapt_stage.c`
composes the active `0x1000d8ce..0x1000db34` path through statistic, dot,
coefficient update, second matrix call and residual conversion. Host fixtures
check these leaves separately and the composed active/inactive path.

The native `0x1000e0b8` matrix leaf reads row count from caller stack+8
without a prologue push, making it the seventh C argument. The leaf and
composed callers now retain both unused earlier stack words; matrix and
stage host fixtures pass with this corrected ABI. The current coherent
CK804EF receipt is `build-adapt-stage-round/receipt.json`, 216 units,
11 true imports, linked SHA-256
`802be145e5a1a489fffbca0fc414ef7af2b0da48dc58ee4e3a51a78afa096c9a`.
The full process entry, inactive continuation at `0x1000dd64`, later FFT/output
copy path from db34 and native FP exception/stack bounds remain open.

The output preparation at `0x1000db5c..0x1000dba2` now uses the selected
DSP halfword clear/copy leaves with the native frame-index multiplication and
returned byte offset. The per-channel `0x1000dbc2..0x1000dc94` slice now
decodes peak headroom, shifts the Q15 channel in place, calls the experimental
full energy helper with explicit first-use RAM state, uses the source-owned
RIFFT descriptor at runtime `0x2001700c`, then applies the native signed-byte
final shift to the transformed output. Its host fixture checks peak/shift,
call ordering and the descriptor identity; the host build disables only the
LP32 structure-size static assertions because it dereferences no descriptor
fields. The actual CK804EF compile retains all assertions. This does not
qualify the FFT numerical result or physical RAM initialization.

`backup_beamforming_process_overlap_add.c` covers the active
`0x1000dc94..0x1000dcc8` branch: unsigned transform halfwords, 32-bit
window words, wrapped product, arithmetic Q15 shift and signed destination
addition. Its fixture checks three samples and the inactive tail branch.
Current separate CK804EF archive is 219 units/11 genuine imports, linked
SHA-256 `5060764721073e8beba708e6d9d47748d5ce9785c31fa4ede6c1ac2f24763489`
at `build-overlap-round/receipt.json`. The original final copy/output scaling
at dcd4..dd44 and the whole d46c loop remain open.

The `0x1000dcd4..0x1000dd44` output tail is now represented by
`backup_beamforming_process_output_finish.c`. It retains overlap samples,
scales the mixed unsigned halfwords with the native Q15 window and truncated
gain, and writes little-endian halfwords at the original caller-output frame
byte offset. Byte writes avoid an unaligned C halfword store or a new
`memcpy` import. Its low-address host fixture passes copy and scaling cases.
The channel loop at
`0x1000dba2..0x1000dcd4` is represented by
`backup_beamforming_process_channel_loop.c`; a host fixture checks three
iterations, source stride, destination stride, call order, and the zero-channel
branch. These chunks use the explicit first-use energy RAM contract.

The coherent separate CK804EF receipt is
`build-channel-loop-round/receipt.json`, 221 target units and 11 genuine
imports, linked SHA-256
`1deeb9c2a6d94b839ac8ba9356ad6114627751a86e7262c0074dfaaba2acd02d`.
The d46c process symbol remains a genuine import: the d46c..db5c branch
composition, inactive dd64 continuation, exact stack/FPU state at reentry,
and whole-call numerical comparison remain to be qualified. The experimental
cc70 energy, ce14 create, and c6e8 angle whole candidates remain unbound
pending their actual full-entry checks. Source-owned initialized data and
final SRAM placement are also open. An estimate for the current GSC frontier
is roughly three to six substantial process CFG/ABI rounds and two to four
angle/create whole-call rounds, followed by a separate data/layout closure;
these are work units, not completion percentages.

The adaptation composition now includes the previously omitted inactive
`0x1000dd64 -> 0x1000da9c` continuation. The native zero-flag and
nonpositive-column branches still execute the second complex matrix and
residual conversion before advancing the outer frame loop. The source no
longer returns early at those branches. The host fixture forces the flag to
zero, clears the matrix output, and confirms that the matrix is rewritten;
active and inactive paths pass. CK804EF
`build-inactive-continuation-round/receipt.json` is source coherent at 221
units, 11 imports, SHA-256
`a53094346b11540e3bd7e1a8d5d5ce5565ba8071ee0dbe1a49b6d33cf09d22ac`.
The remaining whole-entry work is the d46c-d8ce setup/loop composition,
db34-db5c transition, parent frame counters and stack/FPU save/restore,
plus the original whole-call oracle. This correction qualifies the branch
composition fixture, not the complete d46c process symbol.

## Full-entry experimental composition and corrected stack lifetime

Native `0x1000db86` overwrites stack+`0x18` with the output-frame byte offset
computed from original r3 and `ctx+0x10 * ctx+0x08`; the earlier
`ctx+0x04 - 1` value is dead by `0x1000dd06`. The prior output-tail source
and odd-offset claim were incorrect. The corrected tail takes the live frame
offset explicitly, and its fixture now tests a reachable even offset. The
frame-state source tracks stack+`0x10`, `0x1c`, `0x20`, `0x2c`, `0x38`, `0x40`,
and `0x44` across `0x1000db34..0x1000db5c`. The diagonal and first matrix
stage now use stack+`0x20`'s per-frame selected coefficient offset, which
increments by `(2 * ctx+0x04 * ctx+0x1c) * 4` at each frame transition.

`backup_beamforming_process_frame_loop.c` composes the per-frame diagonal,
pack, first matrix/residual, conditional adaptation, second matrix/residual,
and frame advance. `backup_beamforming_process_post_ring.c` composes that
loop with output preparation, channel FFT/overlap, and final output. The
experimental whole-entry source composes band selection, ring preparation,
per-stage threshold/average/counter and the post-ring path while exposing
the two observed RAM words as parameters. Host fixtures verify two-frame
offset/call order and two-stage ring/call order. The native nonpositive
ring-column path at `0x1000dd6e` also rejoins division and counter update;
the prior early-return source was corrected and its host fixture passes.

The coherent `build-whole-scaffold-round/receipt.json` has 225 CK804EF units,
11 genuine imports, linked SHA-256
`1dc409fc085b915cefe7fe34098455e3931d4745b3b573b41a9be5c214f6188b`.
This experimental composition is source code, but the original d46c symbol
remains imported. Whole-call native comparisons, exact four-register entry
binding to RAM, FP exception/state behavior, and source-owned initialized
data/final SRAM placement remain unqualified. An updated estimate is roughly
two to four substantial process whole-call/ABI rounds, two to four angle and
create rounds, then a separate data/layout closure.

## Original stock versus source entry in CK804EF QEMU

The first whole-call emulator comparison exposed another live-stack mistake.
Native `0x1000db78` stores **prefill** (`ctx+0x10 * ctx+0x08`) at stack+`0x1c`;
`0x1000db7e` then adds tail only in a transient register for the clear call.
The final `0x1000dcd4` copy starts at mixed+prefill and emits exactly prefill
output halfwords. The earlier C tail used prefill+tail, falsely copying later
samples and writing output when stages were zero. The output source, leaf
fixture, and experimental full composition now use the native live stack
value. The previous 220-225-unit receipts before this correction do not
qualify this output branch.

`verify_process_whole_qemu.py` builds an oracle ELF containing the sealed stock
image solely as a test target and a separate source ELF from the 225 selected
image-B C units. It runs both on pinned XuanTie QEMU SHA-256
`9fbb51168ef087533e8436a3e020962214a6145b33c7398903d08025b753e304`,
CK804EF, virt RAM. Two finite whole-call cases pass with identical observed
states: zero stage/frame with zero output, and zero stage/frame with nonzero
tail copy; both exit 0 after checking scratch clear, retained source data,
and unchanged output. The source test ELF contains fail-on-use witnesses for
the two still imported FP-environment functions; neither was reached.
The exact result and ELF hashes are in `native-oracle-run/receipt.json`.
The coherent target archive receipt is
`build-native-oracle-correction-round/receipt.json`: 225 units, 11 genuine
imports, linked SHA-256
`da821ecc8170c41d0aee9807cbc93a49b5d17c81616e0f5048f9888bb4ddb326`.
These cases do not exercise active ring, frame, FFT, output scaling, or FP
exception paths. Original four-register binding of the two RAM words and
whole-image initialization/layout remain open; the d46c symbol remains a
genuine import. The process frontier is now active stage/frame fixtures,
followed by numeric DSP/FP and ABI/layout qualification. Create and angle
whole-call paths are separate open work.

## Create and nonzero angle whole-call FP frontier

Additional original-image CK804EF QEMU calls use an explicit, test-only
allocator/free table at the native product-operations address `0x2002d7a4`.
Original create `0x1000ce14` with the positive fixture allocates 17 records,
releases one, writes frame size 512, and exits 0. Original angle `0x1000c6e8`
with one 30-degree angle allocates/releases six records, sets ready, writes
the angle float bits `1057360530`, and exits 0. The corresponding C whole
candidate calls both reach `__fe_getround` in `adddf3.o`; the test-only witness
exits 90 before output qualification. `whole_call_fp_frontier.json` records
these exact observations. The witness is not a firmware implementation, and
the selected candidate still imports both FP-environment functions. The
positive native outcomes establish usable fixtures, not whole-body source
equivalence. Resolving the C-SKY rounding-mode and inexact-flag ABI, then
comparing numerical state and allocations, is the next required qualification.

An additional oracle-only probe reads FCR[25:24] through the target compiler's
VDSP builtin and maps C-SKY codes `(nearest, toward zero, up, down)` to the
pinned LLVM compiler-rt enum `(nearest, down, up, toward zero)`; a volatile
inexact arithmetic probe lets the finite calls continue. Under CK804EF QEMU,
the source create and 30-degree angle fixtures then emit exactly the same
observed labels and exit 0 as stock. This is a bounded emulator comparison.
Both probe implementations remain outside the selected 225-unit archive, and
the image still imports `__fe_getround` and `__fe_raise_inexact`. The pinned
QEMU `target/csky/op_helper_v2.c` has a FIXME for FCR rounding behavior, so
device FP flags and directed-rounding behavior require further evidence.

## Pinned C-SKY floating-point environment provider

The official glibc C-SKY port at tag `glibc-2.39`, commit
`ef321e23c20eebc6d6fb4044425c00e6df27b05f`, is now pinned as
`third-party/csky-glibc-fenv`. Its `fpu_control.h` assigns FPCR to
`cr<1,2>`, FESR to `cr<2,2>`; `bits/fenv.h` assigns the four FCR modes; and
`fraiseexcpt.c` raises inexact with an FPUv2 single-precision divide of
1 by 3. The selected C unit `backup_fp_environment_csky.c` adapts exactly
these hardware contracts to LLVM compiler-rt's different enum order. The
target compiler emitted `mfcr cr<1,2>` and `fdivs fr0,fr0,fr1` in this unit.
Direct CK804EF QEMU checks yielded mode sequence `0,3,2,1`, inexact FESR
`0x9000`, exit 0. Linking the real source unit into the finite create and
30-degree angle fixtures yields the same observed labels and exit 0 as the
original image. The coherent `build-fenv-source-round/receipt.json` contains
226 units, nine genuine imports, linked SHA-256
`3c2bdb166b1c1c5d6e90237bfca7e806ae118fb9fec2cd6b68e28883155a1249`.
The QEMU FCR rounding FIXME still limits directed-rounding and hardware
claims. Full create, angle and process imports remain genuine because their
other branches and live product data are not yet qualified.

## Active whole-process QEMU qualification

The first active native fixture hung and hit invalid interrupt-controller
offsets. Address breakpoints localized it after stage/ring work, inside the
channel FFT path from native `0x1000dbc2` toward `0x1000dc94`. The native
call reads the inverse RFFT profile at runtime `0x2001700c`; the oracle had
loaded the stock IRAM image but had not performed the authenticated startup
copy of initialized data from `0x10016f60..0x1001708b` to
`0x20016f60..0x2001708b`. This omitted state, not a decoded process branch,
caused the emulator failure. The test harness now performs that copy only
for the original image before installing its test callback table. The source
ELF continues to use its typed profile and tables.

`verify_process_active_qemu.py` builds source-coherent ELFs from the 226-unit
receipt and runs three finite original/source whole calls on pinned CK804EF
QEMU: the positive 2-microphone/3-stage context, a one-stage short band, and
the positive context with explicit nonzero input impulse. All three produce
identical observed traces and exit 0. The traces include active-stage count,
frame count, allocation/release counts, ring counter, two scratch halfwords,
output hash, transformed first word, and processed-input hash; the impulse
fixture confirms an input halfword of 4096 immediately before process.
Full ELF hashes and traces are in `native-oracle-run/active-receipt.json`.
These particular zero-initialized product buffers yield zero output and
transformed/input hashes after processing, so they do not qualify numerical
agreement for varied live input or FP exception behavior. The original
four-register binding, source product data placement, failure branches and
hardware behavior remain open. The `0x1000d46c` import stays genuine.

## Native trig correction and broader angle fixture

An original/source whole-angle fixture that actually generates one frame's
phase table exposed a semantic error absent from the earlier 30-degree scalar
check: the original table began with `1.0, -0.0`, while C began with
`-0.0, 1.0`. Native instructions identify `0x1000fb14` as cosine (its
small-argument branch calls kernel cosine `0x1001106c`) and `0x1000fbb0` as
sine. The historical address-labelled C function names implied the reverse.
`backup_trigonometry_fdlibm.c` now preserves those ABI symbol names while
implementing the actual native operations, including signed zero in sine's
tiny branch.

The source-coherent `build-trig-correction-round/receipt.json` has 226 units,
nine genuine imports, linked SHA-256
`d6a7eb922f6c5a4468cb1305c741142e2bf792fa4acf909c47e43283c507a0c5`.
`verify_angle_qemu.py` compares complete original/source calls for one angle,
three angles (-30, 0, 30 degrees), ready state, one-frame phase-table
generation, and the alternate geometry branch with and without a frame.
All six traces and exits match, including 16 table words and a
256-byte table hash; `native-oracle-run/angle-trig-receipt.json` binds ELF and
source hashes. The three active-process fixtures also pass unchanged against
this corrected source receipt (`native-oracle-run/active-receipt.json`).
These finite paths do not qualify all angle counts, table extents, numerical
inputs, product data, or hardware FP behavior. The three core provider imports
remain genuine and whole image source/data/layout completion is false.

## Extended active process and create failure frontier

The active-process oracle now includes a full-buffer DC input, an explicit
nonzero overlap-history buffer, a high native gain field, and eight repeated
process calls with both DC input and history. All these original/source traces
match. The history path produces a nonzero internal mixed halfword, and the
eight-call path advances the native/source ring count to 24. Its final caller
output remains zero. The observed mixed halfword is 1 while the matching
window halfword at index 256 is 32560; native Q15 multiply shifts their
product right by 15, yielding zero before output gain. The upstream DSP
matrix/FFT state still needs an attributable nonzero-output fixture; this
oracle cannot establish general numerical equivalence from zero output.
The full multi-case trace receipt is `native-oracle-run/active-receipt.json`.

`verify_create_qemu.py` separately confirms the positive native/source
whole create call: 17 allocation requests, one release, 512-frame result,
matching trace and exit (`native-oracle-run/create-trig-receipt.json`). Its
expanded trace compares every allocation size, sampled forward/inverse
window words, the full 2048/3072-byte window hashes, and the seeded
3084-byte table hash. The original create oracle now performs the authentic
0x12c-byte initialized-data copy before native trig calls; without that
copy, the native kernel reads zero coefficients from RAM 0x20017034 and
produces a false discrepancy. The resulting complete buffer hashes match.
A direct diagnostic of the binary64 kernel at reduced pi/4 initially differed
by two low mantissa units between original and C after this copy. The cause
and corrected-source result are recorded below. A
test-only failed final temporary allocation reaches the native branch
`0x1000d0c2 -> 0x1000d1e2` in disassembly. The subsequent stock diagnostic
transport hangs under this fixture's uninitialized QEMU peripheral state.
The source chunk has host request/null/log tests, but a full native/source
failure-call comparison is still open. The initial context-allocation null
path is an authenticated native dereference fault, not an invented API
failure return. Neither failure path is counted as a whole-call QEMU pass.

## Product-initialized nonzero DSP output

The earlier active fixtures omitted two source-backed product initialization
operations. Native `0x1000b800` calls angle initialization with 35, 45 and
55 degrees and then `0x1000d1fc` to assign the IMCRA work-buffer region
pointers. The test fixture now calls the original or C whole-angle body and
applies the exact authenticated `0x1000d1fc` offset arithmetic to a
test-owned work buffer. It applies the layout directly in the fixture because
that native body logs through a peripheral not initialized by this isolated
QEMU test. The layout C provider remains separately source owned; this
test-only setup is not a firmware substitute.

With DC input, nonzero overlap history, and an explicit gain word, the
original and C create/angle/process whole-call chain now yields the same
**nonzero** caller output: first output halfword 55656, 4096-byte output
hash 1916551535, angle status 0, 23 allocations, seven releases, and ring
count 3. The pinned original/source ELF traces are in
`native-oracle-run/active-receipt.json` under `active_product`. Other
fixtures still exercise distinct zero-output and eight-turn paths. This
qualifies one realistic product-initialized numerical path in QEMU; other
inputs, failure paths, hardware FP behavior, ambient memory ownership and
final image placement remain open. The three core imports stay genuine.

## Native S1 coefficient correction

The two-ULP kernel discrepancy came from a concrete coefficient mismatch.
Native `0x10011012` materializes positive S1 as binary64
`0x3fc5555555555554`; the attributed upstream fdlibm source literal in
`backup_trigonometry_kernel.c` encoded magnitude
`0x3fc5555555555549`. The native tail branch multiplies by positive S1
and adds the product before subtracting from the input. An oracle-only
ordered implementation using the stock coefficient reproduces the native
binary64 result exactly. A separate six-operation native versus selected
compiler-rt add/subtract/multiply fixture also matches (`native-oracle-run/
kernel-arithmetic-receipt.json`), ruling out those sampled primitive calls
as the cause.

The selected C kernel now uses exact negative S1
`-0x1.5555555555554p-3`. Coherent target receipt
`build-kernel-s1-round/receipt.json` contains 226 units and nine genuine
imports, linked SHA-256
`aa9ae4ab78a1e01ad9825b239c352741703c269e0b06a401acba1fab26a83deb`.
The direct reduced-pi/4 original/source kernel result now matches in
`native-oracle-run/create-kernel-detail-receipt.json`. The complete
positive create buffer comparison, six angle cases, and eight active process
cases also pass on this source receipt. This bounds exactness to tested
operands and paths; broader binary64 and hardware FP qualification remains
open. Full image source/data/layout completion remains false.

`verify_trig_grid_qemu.py` additionally calls both direct native/source
binary64 trig entries for 16 chosen inputs: signed zero, tiny positive,
pi/4 threshold neighbors, pi/2, pi, 2pi, ±larger finite values, and
negative quadrants. With the authenticated native CRT copy, all 32 direct
results agree bit for bit (`native-oracle-run/trig-grid-receipt.json`). This
widens finite range-reduction coverage; it does not establish arbitrary
input or hardware FP equivalence.

## Expanded angle-table state check

The earlier eight active-process comparisons observed caller output and selected
state words, not the entire angle table. A stronger product-like angle fixture
with two microphones, three angles, two frames, and a nonzero phase increment
exposes a selected-source defect. The first frame agrees; the second frame's
complex table differs. The stock 96-byte table hash is `-2039930534`, while
the frozen 226-unit C candidate gives `1657662814`. The test is reproducible
with `verify_angle_qemu.py` and `-DANGLE_PRODUCT`. Thus the prior
`active_product` output match remains only a bounded caller-output result;
it does not qualify whole angle or process state.

Direct native instructions `0x1000cb3a` and `0x1000cb5a` identify two C
errors: the phase scratch is the first angle allocation (`r17`), and the
inner microphone loop repeatedly loads the scalar `matrix[angle]`, rather
than `matrix[angle*mic_count+mic]`. Both are corrected in the selected C.
The fresh coherent target receipt `build-angle-table-correction-round/receipt.json`
has 226 units, nine true imports, and linked SHA-256
`878efc6285d72546eca2bc538875f98151551fe2279a336d5611039f10b9e4ec`.
The strengthened seven-case angle oracle now passes, including a hash over
the 96-byte two-microphone/three-angle/two-frame table. An expanded active
product diagnostic also matches every one of its 118 emitted labels,
including the full 12,336-byte angle-table hash `1379608022`, selected
256-byte slice hashes, temporary allocation words, and nonzero caller
output. The normal nine-case active regression passes on the same receipt.
An eighth fixture used a two-microphone, three-angle, two-frame
geometry-mode path with the product 0.035f microphone distance and exposed
another actual discrepancy: all six temporary
allocation prefixes matched, but the native complex imaginary words used
different signed-zero/orientation than selected C. Native `0x1000ca20` then
`0x1000ca26` places the two products in the opposite `fmscs` order from
the compiled C normalization. The corrected C expression now reproduces
the native instruction result. Coherent target receipt
`build-angle-geometry-orientation-round/receipt.json` has 226 units, nine
true imports and linked SHA-256
`48f8a71ff181086b4f123ce5771b35ff4628d6e6a536d0e40fa14ce5a9a13ce9`.
All ten angle fixtures, including three-microphone nonzero and geometry
paths with hashes over the 144-byte tables, and all nine active process fixtures
pass on this receipt. The full 12,336-byte product angle-table diagnostic again matches
all 118 emitted native/C labels, including hash `1379608022`.
The one positive whole-create fixture and direct 16-input-per-function trig
grid also pass after rebuilding their test ELFs from this final receipt.
For the product-initialized angle call, `verify_product_table_bytes_qemu.py`
also emits all 3,084 table words from each QEMU run into separate binary
files and compares every byte. All 12,336 bytes agree; both table files have
SHA-256 `dc9f9efea3c031390778627302d1942d9887ed0b29e6f38c40a5822995e44b0f`
(`native-oracle-run/active-product-table-byte-receipt.json`). This direct
comparison is limited to that one fixture and does not imply an arbitrary
input or hardware FP proof.

Two further direct-byte oracles use the same 226-unit source receipt.
`verify_create_buffers_bytes_qemu.py` compares all positive-create forward
window (2,048 bytes), inverse window (3,072 bytes), and steering table
(3,084 bytes), with no differing byte (`native-oracle-run/
create-buffer-byte-receipt.json`). `verify_process_output_bytes_qemu.py`
compares all 4,096 bytes of one nonzero active-product caller output; native
and C SHA-256 are both
`4783c97da3a3cfe9734cfb6947a4439ab9de30e2741293fed3e806ca30eacb6c`
(`native-oracle-run/active-product-output-byte-receipt.json`). These are
full-buffer comparisons for finite calls, not full internal-state or
hardware equivalence.

The positive-create whole-call fixture also passes a second ABI/data point:
8-kHz sample rate with one microphone, three angles, and output index zero
(`native-oracle-run/create-trig-receipt.json`). The product case remains
16 kHz, two microphones, and output index one. Both have matching native/C
allocation counts, sizes, selected window words, and buffer hashes; the
direct three-buffer byte receipt above covers the product case only.

These finite comparisons repair both observed discrepancies without
qualifying arbitrary numerical input, hardware FP behavior, failure
transport, data ownership, or final loaded-image layout. The three GSC
core imports remain genuine until full contract qualification.
