# G2 Apollo LC3 `service_audio` stock-ABI route boundary

Status date: 2026-08-30  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Result: exact software route and relocation replay qualified; production
placement and firmware patching remain blocked

## Exact stock ABI

The route replaces two complete stock entries, rather than attempting to map
the five low-level liblc3 calls directly:

| Stock entry | ABI | Whole-image ingress |
|---|---|---:|
| `0x0057A926` | `void setup(void *context)` | 4 |
| `0x0057A940` | `int encode(pcm, uint32 bytes, output, int32 *written, context)` | 5 |

Every ingress is an authenticated Thumb `BL`. Each caller obtains its context
from one of five authenticated literal cells; together they name exactly the
four contiguous 2,628-byte states at `0x20106A7C`, `0x201074C0`,
`0x20107F04`, and `0x20108948`. There is no additional whole-image direct
ingress to either entry and no unknown context at an admitted callsite.

The future entry patches are four-byte Thumb-2 `B.W` tail branches. A normal
`BL` at the entry would return into the displaced stock body, so it is
explicitly rejected. The tail branch preserves the link register established
by every existing caller and lets the maintained shim return directly to that
caller.

## One-way state transition

`runtime_liblc3_service_audio_stock_shim.c` accepts only the four exact context
addresses. On first setup or lazy encode it copies the 24-byte stock
configuration, requires the stock cached encoder pointer at `+24` to remain
zero, validates the complete runtime geometry, and converts the same slot to
compact adapter control. Owner tokens are derived uniquely from slot index.

An unsupported configuration or provider setup failure restores the complete
stock header and zero cached pointer, allowing a later legitimate retry.
Once compact state is valid, query and encode rederive the sealed provider
view without codec reinitialization. A corrupt compact state is not silently
reset. State, PCM, output, and output-count aliases fail closed; provider
failure preserves the completed output prefix and invalidates the lifetime.
An explicit call to the stock setup entry remains an unconditional codec
reset, matching the recovered body: the shim snapshots the sealed config,
closes, and reopens the same owned slot. Host tests prove that generation and
provider-setup count both advance on repeated setup.

## Integrated build and relocation replay

`build_service_audio_route_experiment.py` compiles the shim, adapter, provider,
and 11 specialized encoder units, applies the authenticated immutable-table
conversion, and calls the existing component finalizer at a deterministic
synthetic layout. Both reviewed profiles build twice byte-identically and emit
no unresolved symbol or retained relocation:

| Profile | Relocatable | Text | RoData | Tables | Relocations | Residual shortfall |
|---|---:|---:|---:|---:|---:|---:|
| Apple Clang 21 | 121,212 bytes, `826c061f89d13fba323ab3ccff826c105c7dde4dcdf764c133c4680ef0cd512b` | 44,432 | 60,336 | 404 | 515 | 34,084 |
| Homebrew Clang 22 | 122,364 bytes, `020fa988928a6b70261c20fc3fb8a881d16f8350afe607eba00a0f027024aa4c` | 45,552 | 60,336 | 404 | 521 | 35,204 |

The runtime import set remains the specialized encoder's exact 11-symbol
allowlist. Apple synthetic finalization emits a 182,072-byte ELF with SHA-256
`546cc5e9f078aa7f8a8cf0726de338595a0964850178ee63b2273c37931d45ea`;
Linux emits 183,192 bytes with SHA-256
`cdcf854cd42fa42c27bb9d23c129be3f53530c684b1e50e31738c83b0c5db8e7`.
All table words and all input relocations are verified before XIP bytes are
emitted.

## Fail-closed outcome

The canonical Apple closure spans 105,184 aligned append bytes, while only
71,100 authenticated bytes remain before protected `0x007FE000`. Its exact
shortfall is therefore **34,084 bytes**, 3,568 bytes more than the encoder-only
shortfall. Synthetic veneer encodings are proof vectors, not production patch
bytes. No stock runtime address, stock runtime-symbol binding, core overlay,
package manifest, flash plan, or firmware image was modified.

`service_audio_routed`, `production_placement`, and `firmware_image_emitted`
remain false. No hardware, acoustic, timing, stack, BLE interoperability,
power, or flash operation was attempted.

## Reproduction

```sh
python3 g2/tools/analyze_g2_liblc3_service_audio_route.py --pretty
python3 -m unittest -v g2.tests.test_runtime_liblc3_service_audio_stock_shim
python3 -m unittest -v g2.tests.test_analyze_g2_liblc3_service_audio_route
```

The machine-readable admission is
`components/apollo_main/liblc3_encoder/service_audio_route_experiment.json`.
