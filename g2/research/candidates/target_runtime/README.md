# G2 shared target-runtime source-admission candidate

The scalar source and header in this directory are licensed under MIT. The
Arm EABI bridge is GPL-3.0-only because it binds the exact compiler entry to
the existing GPL-3.0-only division-free provider in
`components/apollo_main/core_overlay/aeabi_divmod.c`. No upstream liblc3 or
FreeType source is copied or modified here; their Apache-2.0 and FTL terms
remain intact.

This is an isolated, production-excluded Cortex-M55 link harness for the
liblc3 and FreeType source-admission candidates. It is not a selected firmware
libc and is not referenced by an overlay or production build file.

## Closed provider set

`runtime_target_scalar_candidate.c` supplies inspectable scalar definitions
for the ordinary ISO C memory, string, and sort surface used by the two
candidates. It also supplies the single-precision IEC 60559 operations used by
liblc3. `sqrtf` uses the Cortex-M55 scalar floating-point square-root
instruction; the host path exists only for semantic qualification. The Arm
EABI memory entries are thin calls into the same scalar cores.

The exact `__aeabi_uldivmod` entry is a tail bridge to the existing
`open_cfw_aeabi_uldivmod` provider. That provider performs division-free
restoring long division and explicitly marshals the four-register Arm EABI
quotient/remainder result. This avoids substituting a normal C 64-bit division
whose compiler lowering would recurse back into `__aeabi_uldivmod`.

The existing reconstructed IAR memory functions were reviewed but not reused:
they intentionally advance `r0` and expose a void contract, while ISO
`memcpy`/`memmove` must return the original destination. The reconstructed IAR
`sqrtf` was also not reused because its domain path writes errno to a fixed
stock-image RAM address. Neither behavior is suitable for a shared relocatable
provider.

The target gate compiles every liblc3 and selected FreeType translation unit
to Cortex-M55 hard-float LLVM objects, links them with the providers, and
queries the linked module rather than merely unioning source declarations.
The FTL system adapter now closes `FT_New_Memory`, `FT_Done_Memory`, and
`FT_Stream_Open` through configure-once allocator and immutable byte-view
resolver ports. The authenticated selection does not contain the optional
gzip implementation, so its controlling option is explicitly disabled; a
compressed WOFF table returns FreeType's upstream `Unimplemented_Feature`
path rather than calling an invented decompressor.

The MIT-licensed clean-room provider at
`../freetype/runtime_freetype_jump_candidate.c` closes
`open_cfw_freetype_external_setjmp` and
`open_cfw_freetype_external_longjmp`. Authenticated stock leaves and the
FreeType validator layout establish the 128-byte, eight-byte-aligned ABI, the
saved `r4-r11`, `sp`, `lr`, and `d8-d15` state, and the required zero-to-one
return normalization. `../freetype/JUMP_ABI_EVIDENCE.md` records the bounded
image hashes, direct-call topology, and clean-room derivation. The linked
Cortex-M55 candidate graph consequently has no unresolved symbols.

This is software link closure, not production admission. Remaining
qualification is scheduler policy forbidding jumps across task or exception
boundaries, stack/WCET review, and final toolchain/link placement.

Run the focused gate with:

```sh
cd g2
python3 -m unittest -v tests.test_runtime_target_provider_candidate
```
