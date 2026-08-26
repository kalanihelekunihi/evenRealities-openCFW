# G2 IAR formatted-output source closure

Scope: authenticated G2 `2.2.6.10` Apollo-main image. Status: the complete
production-reachable formatted-output graph is implemented in maintained,
freestanding C and included in the deterministic firmware image. Physical
execution remains blocked by unavailable authorized responsive hardware. No
image was signed, flashed, or installed.

## Production route

The four exact stock wrappers at `0x0044B728`, `0x0044B76C`, `0x004B4728`,
and `0x00595A34` all call the sole IAR formatter core at `0x00481836` and all
pass `secure = 0`. Their wrapper-owned buffer/stream state, termination, and
return contracts remain unchanged. The entire 3,256-byte core is SHA-guarded
and redirected with a non-linking Thumb-2 `B.W` to
`open_cfw_runtime_iar_printf_core`.

The source-owned route consists of:

- `open_cfw_runtime_iar_printf_core`, an exact soft-PCS ingress for IAR's
  argument cursor;
- `open_cfw_runtime_iar_vformat`, which validates the writer, format, and
  non-secure contract;
- `open_cfw_runtime_iar_format_bridge`, which preserves the stock
  `(state, character) -> next_state` writer ABI and suppresses only the
  formatter's synthetic terminator while retaining an actual `%c` NUL; and
- `open_cfw_runtime_iar_vsnprintf_engine`, a maintained mpaland-derived
  freestanding formatter specialized for this ABI.

The engine implements flags, width, precision, `*`, integer and pointer
formats, `hh/h/l/ll/j/t/z/q/L` modifiers, strings, characters, `%n`, `%f`,
`%e/%E`, `%g/%G`, `%a/%A`, infinities, NaNs, binary64 subnormals and
round-to-nearest-even hexadecimal precision, plus the recovered `%PV`/`%pV`
recursive descriptor extension. `q` maps to the IAR 64-bit integer slot and
`L` consumes the same aligned binary64 slot observed in stock.

Annex-K output behavior is not claimed. Exhaustive wrapper decompilation shows
there is no secure ingress in this image; every stock wrapper supplies zero.
The source adapter nevertheless rejects any nonzero secure flag with `-1`, so
an unreviewed future route fails closed instead of silently claiming
`printf_s` semantics.

## Deterministic artifacts

The reviewed Apple-Clang target build places four strict leaves at:

| Leaf | Overlay offset | Runtime address | Bytes |
| --- | ---: | ---: | ---: |
| `open_cfw_runtime_iar_vsnprintf_engine` | 404,796 | `0x007F7060` | 3,512 |
| `open_cfw_runtime_iar_format_bridge` | 408,308 | `0x007F7E18` | 50 |
| `open_cfw_runtime_iar_vformat` | 408,360 | `0x007F7E4C` | 84 |
| `open_cfw_runtime_iar_printf_core` | 408,444 | `0x007F7EA0` | 14 |

The engine has exactly 11 authenticated relocations to already source-owned
formatter helpers. The resulting identities are:

- overlay: 408,458 bytes, SHA-256
  `22a9e111e2b790489c50b0c631f87150b4d93a82b40539dae1509fd631248c18`;
- Apollo component: 3,931,854 bytes, SHA-256
  `8e217faf212b5cf397b19ce0648c665b3f62233be67e418fba35abccc5672763`;
- complete EVENOTA: 4,710,348 bytes, SHA-256
  `fab299362ebbeff5b0e31923ea3aae7b6c20a3d87983a20ab964f13540ffbaee`;
- flash plan: 4,071,802 bytes, SHA-256
  `fd12c956d57ff02be8fc82545f2ff189dd8f04babb52cfbe29dd1d84617d983d`,
  with 5,864 placed, two unresolved, five container-only, and six protected
  regions.

`make iar-format-output-closure` rebuilds the full package and runs host ABI,
format-semantics, target compilation, relocation, redirect, manifest,
package, and flash-plan gates.

## Hardware block

On-device validation requires a responsive authorized right temple to exercise
bounded/unbounded/default-stream writers, dynamic formats, floating-point
rounding, writer failure, and wrapper termination. That temple is
nonresponsive, the left temple must remain stock, and no equivalent authorized
responsive G2 is available. This is an explicit unavailable-physical-evidence
block, not a software gap. Wider firmware functional completeness is not
claimed.
