# G2 FreeType base-module source candidate

License: FreeType Project License (`FTL`). The unmodified license is retained at
`g2/third_party/freetype/LICENSE`. Portions of this candidate are based on the
work of the FreeType Team.

This production-excluded candidate binds the authenticated FreeType 2.9.1
snapshot to the recovered G2 allocator and lifecycle shape. It is intentionally
stored under `research/candidates`: the snapshot verifier rejects all FreeType
references under production components.

## Closed tranche

The base-module census has ten high-confidence entries:

1. `FT_Init_FreeType`
2. `FT_Add_Default_Modules`
3. `FT_Add_Module`
4. `FT_New_Library`
5. `FT_Open_Face`
6. static `open_face`
7. `FT_Done_Face`
8. static `destroy_face`
9. `ps_property_set`
10. `ps_property_get`

The bounded tranche admits all 17 direct-call-graph rows plus all 56
semantically pinned indirect loader/slot/fallback/stream/memory/renderer/module
rows to named, hash-authenticated upstream definitions. Together with these ten
anchors, all 83 base-community functions are source-admitted, covering all
7,874 official bytes. `BASE_CLUSTER_ADMISSION.md` records the entry map and
evidence, including the literal-level distinction between the otherwise
byte-shape-identical AppleDouble and AppleSingle wrappers.

The host gate executes the public paths covering this set: both conventional
`FT_Init_FreeType` and the custom-memory `FT_New_Library` path, exact ten-module
registration, CFF property set/get, invalid and valid memory-face open paths,
and explicit face destruction. A deterministic one-empty-glyph TrueType font
is constructed by the test itself; no unknown G2 font payload is claimed.

`runtime_freetype_base_candidate.c` recreates the recovered Even sequence:

```text
allocate FT_MemoryRec -> install allocator callbacks -> FT_New_Library
                      -> FT_Add_Default_Modules
```

Candidate storage must be zero-initialized with
`OPEN_CFW_FREETYPE_BASE_CANDIDATE_INIT` before first use.

On the 32-bit target, `FT_MemoryRec` is statically pinned to 16 bytes with its
four pointer fields at offsets 0/4/8/12. Every FreeType allocation passes
through caller-supplied allocate/reallocate/release ports. Teardown uses the
upstream `FT_Done_Library` and only then releases the separate memory record.
This is an explicit community-firmware lifecycle; the stock image has no safely
assignable conventional `FT_Done_FreeType` entry.

Stock clears `FT_MemoryRec.user`; this multi-instance adapter deliberately uses
that public field to recover its owning port context inside the three callbacks.
That is an explicit source-level adaptation, not a claim of byte identity with
`am_ftsystem.c`.

The recovered module order comes from the existing authenticated
`third_party/freetype/g2-config/freetype/config/ftmodule.h`. The local
`g2_config` wrapper preserves upstream `ftoption.h`, disables the stock-proven
absent environment-property parser, and fails compilation if any other proven
G2 option drifts.

## Qualification and remaining work

The candidate, base tranche, bitmap helper, and all ten selected module
translation units compile independently for Cortex-M55 Thumb hard-float. The
bare-target headers in `target_compat` are declaration-only compile boundaries,
not implementations or a selected libc ABI.

The isolated shared-runtime harness closes lifecycle/system, memory/string,
sort, and compiler helper references. `runtime_freetype_system_candidate.c`
provides conventional memory lifecycle and path loading through configure-once
allocator and immutable byte-view ports. Gzip is explicitly disabled because
its implementation is outside the authenticated 297-file selection.

`runtime_freetype_base_cluster_candidate.c` isolates face-loader policy. Its
autodetect mode retains stock's upstream behavior; TrueType-only and CFF-only
use `FT_OPEN_DRIVER` to bypass unrelated fallback loaders for known assets.
The authenticated nine-slot Mac/resource-fork chain is upstream FreeType
2.9.1 mechanics, not opaque Even loader code.

The next non-CFF module tranche closes the authenticated TrueType driver's
complete non-null class surface: 13 callbacks and 1,188 bytes covering driver,
face, size, and slot lifecycle plus glyph loading, metrics, sizing, and service
dispatch. `TRUETYPE_SOURCE_ADMISSION.md` records the class-slot map. Its FTL
adapter uses only public `FT_Property_Set`/`FT_Property_Get` calls to qualify
the stock-proven v40 interpreter default, supported v35 selection, and
fail-closed rejection of unsupported v38.

The first private TrueType closure adds 21 exact upstream helpers and 3,764
bytes below those callbacks, bringing this driver graph to 34 attributable
functions and 4,952 bytes. The analyzer keeps its ten-function second-level
frontier explicit instead of inferring ownership from address order.

The MIT-licensed `runtime_freetype_jump_candidate.c` closes the typed
`open_cfw_freetype_external_setjmp` and
`open_cfw_freetype_external_longjmp` boundary. Authenticated stock leaves and
the FreeType validator layout establish a 128-byte, eight-byte-aligned buffer,
the complete saved-register set, and return semantics. The provider compiles
to the exact observed leaf bodies; `JUMP_ABI_EVIDENCE.md` records the hashes,
call topology, and clean-room boundary. The complete selected Cortex-M55 graph
now links with zero unresolved symbols.

Further production blockers are the unproven FreeType configuration options
outside the recovered subset, exact IAR/link flags and section budget,
stack/WCET qualification, scheduler policy ensuring non-local jumps never
cross task or exception boundaries, and the absent external G2 font payload
identities and runtime face-path arrays.

Run the isolated gate with:

```sh
cd g2
python3 -m unittest -v tests.test_runtime_freetype_base_candidate
```
