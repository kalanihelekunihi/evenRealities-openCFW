# Nanopb private `pb_decode_inner` source audit

This audit promotes the complete G2 private decoder loop. Its helper entry
addresses preserve the stock ABI, but every executable helper entry used by
this loop is now guarded and redirected to a reviewed source-owned leaf. Schema
descriptors and application callbacks remain external data/callback seams.

## Authenticated boundary and source

| Evidence | Pin |
|---|---|
| Official body | `[0x0048FE98,0x00490112)`, 634 bytes |
| Body SHA-256 | `13f2b83cd22ed38a6b74d52b0bd4eb6e8577becdcf5a1c8816a4af6aef1eea52` |
| Direct callers | `0x00490124` (`pb_decode`) and `0x0049051A` (`pb_dec_submessage`) |
| Caller-address digest | `f8fe3e1175baf06e17d29d81e9daaae0d69d0d54c76bbf230f1514dd18c0523d` |
| Upstream definition | authenticated nanopb 0.4.9 commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`, bytes `[32121,37346)` |
| Upstream-definition SHA-256 | `01b0015f6b8450e27d38a5f60e57708d9007d005d9ece2ef3fdb287b27ed23f4` |

Rizin confirms a single Thumb entry and return at `0x00490112`. The analyzer
rejects alternate `BL`, `B.W`, conditional, narrow, and interior ingress.
Nineteen raw four-byte matches are authenticated table/text collisions (16-bit
numeric tables, color-like data, or UTF-16 text), not executable pointers; the
concatenated collision-context SHA-256 is
`7441bc1937158ceb916197b10d97186f3d9a4c1711a76c7823c110e6e202b70b`.

Recovered configuration is `PB_MAX_REQUIRED_FIELDS=64`, 16-bit `pb_size_t`,
`PB_ENABLE_MALLOC` off, `PB_DECODE_NOINIT=1`, and
`PB_DECODE_NULLTERMINATED=4`. The implementation preserves default
initialization, sticky errors, EOF/null termination, extension routing,
fixed-count validation, and the two-word required-field bitmap.

## Dependency closure

| Stock call target | Role | Production ownership |
|---:|---|---|
| `0x004D9384` | `pb_field_iter_begin` | guarded source replacement |
| `0x0048FDF2` | `pb_message_set_to_defaults` | guarded source replacement |
| `0x004D93F8` | `pb_field_iter_find` | guarded source replacement |
| `0x004D946E` | `pb_field_iter_find_extension` | guarded source replacement |
| `0x0048FC88` | `decode_extension` | source leaf at `0x007B3A70` |
| `0x0048F66C` | `pb_decode_tag` | guarded source replacement |
| `0x0048FBE4` | `decode_field` | source leaf at `0x007B39CC` |
| source leaf | `pb_skip_field` | source-owned |

The stock call graph still exposes the original entry addresses, while the
production relocation/patch graph has zero executable stock seams. Seven
guarded entries and two direct overlay bindings close all eight helper
families over source. The stock memory-fill call at `0x0043C0E4` is eliminated
by local initialization. All four diagnostics
(`failed to set defaults`, `zero tag`, fixed-count, and required-field errors)
are source-owned in one 88-byte closure.

## Production placement and status

Apple Clang 21.0.0 emits 530 text bytes at
`[0x007B3120,0x007B3332)` and 88 diagnostic bytes at
`[0x007B3332,0x007B338A)`, preceded by one alignment byte. Text,
unrelocated-text, and closure SHA-256 values are respectively
`bb7c39bf211af376c6c2bed5e718da7e2462847ea1616666eb8f57a287541d86`,
`94760bea8227002de63284f309e2dce73a798932a5dab28e97650cf2695d3035`,
and `6edb8cd4882360355fe16a09acd3fbc4affd24aeb8aeb98b311a0be3c14424f4`.
The full stock span is replaced by a guarded `B.W` and Thumb NOP fill.

Current Apple overlay/component/package pins after closing the dispatch and
extension trio are `128924 / 3652320 / 4430814` bytes. Their SHA-256 values
are `555cee5a2bf43bafef750c77658b654fc72642699d5e432226d209337b69eb57`,
`60d9a28c2dc38e04d2ea3fd6109d7d26b3229d1e0b8ec04a695cde7c3146f4e8`,
and `764b752f15d7cc5a0609091a2c6852aee1a4b1892125b1ac185134ab0897a751`.
Linux/Clang 22 byte reproduction and hardware execution remain deferred.

Reproduce the focused evidence with:

```sh
python3 tools/analyze_g2_nanopb_decode_inner.py --json
python3 -m unittest tests.test_runtime_nanopb_decode_inner
python3 components/apollo_main/core_overlay/build_component.py
python3 tools/open_cfw.py verify --manifest manifests/g2-2.2.6.10-core-source.json
```
