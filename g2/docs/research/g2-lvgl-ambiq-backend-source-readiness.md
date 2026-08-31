# G2 Ambiq LVGL draw-backend source readiness

Status date: 2026-08-30  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Mode: offline source authentication and isolated Cortex-M55 compilation; no
signing, linking into a firmware image, flashing, MMIO, or hardware operation

## Result

The largest actionable LVGL/Ambiq draw frontier is no longer source-opaque.
This tranche imports the exact public `src/draw/ambiq` subtree authenticated by
the retained G2 source paths and diagnostics:

| Source boundary | Result |
|---|---:|
| Ambiq LVGL subtree Git tree | `1e774257495fa43177e04fc5c8a42a77c2d7d619` |
| Canonical public commit | `5be8e0ae5077aa3880aba8a322b1487d6bc73c07` |
| Exact source/header files | 16 |
| Exact source/header bytes | 170,833 |
| C translation units in the exact subtree | 14 |
| Translation units authenticated as linked by G2 | 11 |

The 16 unchanged files are in
`third_party/lvgl-ambiq-backend/src/draw/ambiq`. The existing fail-closed
provenance manifest authenticates every file by size, Git blob SHA-1, and
SHA-256. `border`, `line`, and `vector` are retained as members of the exact
public subtree, but no G2 evidence in the current audit authenticates them as
linked; the builder therefore excludes those three units.

The corresponding public Nema interface is now locally reproducible. The
header-only snapshot in `third_party/nema-sdk-headers` contains 32 exact files
and 251,655 bytes from Ambiq's public NemaGFX SDK state at commit
`b853fded7e545f005727e13bf2ce83018c7e242d`, complete-SDK subtree tree
`e690768a6e7b4d6a8d526fc75e8278a2764deff3`. It reports NemaGFX 1.4.12 and
NemaVG 1.1.8. Its canonical inventory digest is
`186008f77de1bfa3942b4ad0de8f2a8932fcc834558fb1641d87e94f3ccd36a8`.
No Nema implementation archive is imported by this tranche.

## Compatibility seam and compile qualification

`tools/build_g2_lvgl_ambiq_backend.py` authenticates both snapshots before
compiling. It then constructs a temporary hybrid staging tree from the checked
LVGL 9.3-development compatibility ceiling, applies the previously recovered
eight-callback draw-buffer ABI patch, copies the exact Ambiq backend, and
applies a separate, pinned compatibility patch. The exact upstream files are
never edited in place.

The compatibility patch is limited to declaration and C-conformance defects
at this hybrid boundary: the private image header include, base draw-unit cast,
const correctness, a void-return correction, explicit result returns, format
argument widths, image-decoder close pointer depth, C11 switch-case scopes,
redundant conditional parentheses, and two Nema HAL port declarations that the
public `nema_hal.c` exports but its public header omits.
Patch and compatibility-header identities are recorded in
`tools/manifests/g2-lvgl-ambiq-backend-readiness.json`.

The compile gate selects exactly the 11 G2-authenticated translation units plus
the separately pinned cache-free radius-mask provider and uses:

- `arm-none-eabi`, Cortex-M55, Thumb, short enums, GNU C11, `-O2`, and
  function/data sections;
- the actual checked Apollo510, CMSIS, Nema, and FreeType headers;
- the recovered 8-bit color, FreeRTOS, FreeType, Ambiq draw/vector,
  100-by-1,024-byte command-list, and Nema power-save switches; and
- minimal declaration-only C-library/FreeRTOS shims because this isolated
  compile is not a target-runtime link.

Implicit function declarations, incompatible pointer types, missing non-void
returns, and every compile warning are errors. Two independent builds under the
same compiler must produce byte-identical objects and a byte-identical
deterministic archive. The focused test parses all 12 archive members and
verifies that each is an Arm ELF object. The generated archive intentionally
has no symbol index:
it is a compile-qualification container, not a production link artifact.

## Cache-free radius-mask closure

The isolated compile preserves the proven `LV_DRAW_SW_COMPLEX=0` G2 setting and
therefore omits the software circle-mask cache from `lv_global_t`. The exact
LVGL 9.3-development implementation at commit
`344c7c318047b7348e1be8572a9fd4260c251cfa` is preserved under
`g2-compat/upstream` (43,443 bytes, SHA-256
`8a5075210d3a59c4fa7ea00e5675205a6a2e7e8e98305c26045c30c2e77846a6`).
The compatibility provider keeps that raster and four-times antialiasing
algorithm while moving circle ownership from the absent global cache to each
radius parameter. It exports the exact two functions imported by Ambiq box
shadow and depends only on the four LVGL allocation/memory primitives.

Host verification compares all mask bytes and callback results against the
authenticated upstream implementation for 1,505 fixed and deterministic
randomized cases. It also injects failure at each of the three allocations,
checks null/double-free and hostile coordinates/lengths with guard bytes, and
bounds the full-screen-visible radius-144 peak allocation linearly. Allocation
failure is fail-closed: the callback returns transparent without modifying its
output buffer. Cortex-M55 static assertions pin the 36-byte parameter and
28-byte circle descriptor ABIs; symbol and relocation gates prove the box
shadow object has one Thumb call to each provider export and that the provider
has no cache/global-state import.

## Recovered stock draw-thread stack

The official 3,523,396-byte firmware image (SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
authenticates `lv_draw_ambiq_init` at `[0x004C73D6, 0x004C74EE)`. Its AAPCS
thread-call sequence at `[0x004C74CE, 0x004C74EA)` includes
`mov.w r0,#0x8000; str r0,[sp]` before the call to `lv_thread_init`; the stack
argument is therefore exactly 32,768 bytes. The builder pins the complete
28-byte sequence and function hashes, defines `LV_DRAW_THREAD_STACK_SIZE=32768`,
and obtains a warning-free target compile. This is value recovery only:
worst-case use and runtime high-water behavior with FreeType remain unqualified
without an authorized target.

## Reproduction

From `g2`:

```sh
python3 tools/build_g2_lvgl_ambiq_backend.py --json
python3 tools/build_g2_lvgl_ambiq_backend.py \
  --output-dir /tmp/g2-lvgl-ambiq-qualification
python3 -m unittest -v \
  tests.test_build_g2_lvgl_ambiq_backend \
  tests.test_runtime_lvgl_ambiq_sw_mask_cache_free \
  tests.test_analyze_g2_lvgl_ambiq_provenance \
  tests.test_analyze_g2_nemagfx_ambiq_provenance
```

The focused builder test rejects a one-byte mutation to either authenticated
snapshot or stock firmware, reproduces the checked readiness manifest, pins the
compatibility seam, runs the target compile twice, and checks the deterministic
archive. The cache-free runtime test performs the reference parity, allocation
failure, hostile-input, and memory-bound checks described above.

## Remaining admission and physical gates

The source-opacity and isolated-compilation gaps are closed. Production remains
fail-closed on all of the following:

1. resolving the exact atomic-link boundary quantified in
   `g2-lvgl-nema-atomic-link-readiness.md`: the scoped public archives, EVB HAL,
   and two local buffer helpers reduce the missing Nema HAL symbol count to
   zero, but the full target runtime/link and G2-specific port are not admitted;
2. qualifying the recovered 32 KiB draw-thread stack at worst case and runtime
   with FreeType enabled;
3. choosing and qualifying stock-IAR archive compatibility versus a maintained
   GNU/ELF integration route; and
4. validating command-list execution, cache maintenance, power retention,
   antialiasing, and display output on an authorized Apollo510/G2 target.

No authorized physical target identity, transport, captured GPU trace, or
display observation was supplied to this software-only tranche. Consequently
the fourth gate is blocked by unavailable physical evidence. The backend is not
registered in an overlay, and this document makes no claim about live hardware
behavior or a complete functional firmware image.
