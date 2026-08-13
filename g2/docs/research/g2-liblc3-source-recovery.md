# G2 Google liblc3 source recovery

Status date: 2026-08-12  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Result: source family, compatible commit interval, and reproducible tagged
baseline closed; exact producing checkout and target integration remain gated

## Result

The retained first-party object `platform\audio\service_audio.c` directly
calls four public entries from [Google liblc3](https://github.com/google/liblc3):

| Public API | Stock entry | Direct calls from `service_audio.c` |
|---|---:|---:|
| `lc3_frame_samples` | `0x00590E64` | 1 |
| `lc3_frame_bytes` | `0x00590F78` | 1 |
| `lc3_setup_encoder` | `0x00591374` | 2 |
| `lc3_encode` | `0x0059138A` | 1 |

The complete five-edge caller set hashes to
`36909f9489dab1c8f1ef70c8e1e6734fd037f6bded774d1235c2065cc37857b6`.
The wrappers lead into the expected shared LC3/LC3plus helpers, and the
536-byte `lc3_encode` entry has 192 decoded instructions, 18 direct internal
calls, and one format-loader indirect call. This is linked codec code, not an
API-name resemblance in first-party code.

The selected source baseline is official tag `v1.1.3`, commit
`96a3af0beb5487aca3b98a4b992a539a1f6d80d1`, tree
`d5613b74b5d271bb7b263d85d1b9b913b4dfb74b`. The complete 38-file upstream
source/build snapshot is admitted under `third_party/liblc3` and remains
byte-identical to that tree.

## Commit interval

Two independent binary discriminators bound the implementation:

1. Stock contains IEEE-754 `FLT_MAX` (`0x7F7FFFFF`) at `0x0059A9AC` in SNS
   quantization. That selects commit
   `bb85f7dde4195bfc0fca9e9c7c2eed0f8694203c` or later; the commit replaced
   the fast-math-sensitive use of infinity.
2. Encoder setup stores `dt`, `sr`, and `sr_pcm` at byte offsets 0, 1, and 2,
   and encode reads the same layout. Commit
   `9f1e206b34546e858e11065151ae38ff4efc4c77` inserts `ltpf_bypass` before
   those fields and changes the analysis path, so that successor is absent.

The latest proven compatible public state is
`1de85e2d9b8f8f3dffb50f70881b3475bbdfb803`. Its only C delta after v1.1.3
corrects the misspelled, dead-stripped `lc3_frame_block_bytes` definition.
The linked G2 surface therefore cannot distinguish tagged v1.1.3 from that
successor. v1.1.3 is the reproducible tagged baseline, not a claim that the
private Even checkout was exactly that Git commit.

The nearby firmware string `1.1.4` belongs to retained event-loop metadata;
it is not an LC3 version string and was not used as provenance evidence.

## Source admission

`third_party/liblc3` contains the Apache-2.0 license, README, public and
private headers, every implementation source, generated coefficient tables,
and Make/Meson metadata. `SNAPSHOT.sha256` authenticates all 38 upstream files;
`PROVENANCE.json` records Git blob identities, the selected tree, and both
commit discriminators. `verify_snapshot.py` rejects content drift or a changed
selection boundary. The unmodified snapshot also builds successfully with its
host Makefile.

Machine-readable stock evidence is split between:

- `tools/manifests/g2-liblc3-public-entry-map.tsv`, which pins the four public
  bodies and their exact stock hashes; and
- `tools/manifests/g2-liblc3-source-boundary.tsv`, which pins the compatible
  commit interval, layout and constant discriminators, snapshot identity, and
  unresolved exact-checkout status.

`tools/analyze_g2_liblc3.py` authenticates those records against the official
image and admitted snapshot. Run `make liblc3-source-closure` for the focused
verification contract.

## OpenCFW boundary

No third-party LC3 implementation behavior remains opaque for source reuse.
Production routing is intentionally not enabled. It still requires the target
IAR/build-profile decision, Apollo510 floating-point and performance testing,
G2 audio-buffer ownership/integration, and interoperability validation against
known-good LC3 peers. Those are target and hardware gates, not unresolved
family, version, or public-source gaps.

The adjacent `service_audio.c` translation unit remains first-party recovery
work. Its direct codec edges can now terminate at this admitted source rather
than at an unidentified binary provider.
