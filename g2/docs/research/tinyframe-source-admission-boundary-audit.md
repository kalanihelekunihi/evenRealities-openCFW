# TinyFrame G2 source-admission boundary audit

Status: production source admission complete. The authenticated TinyFrame core
and G2 boundary are atomically routed in the Apollo-main overlay and owned by
the firmware manifest. No signer, hardware, or flash state was changed.

Target: official G2 `s200_v2.2.6.10` Apollo-main image, authenticated by
[`../../tools/analyze_g2_tinyframe_send_version.py`](../../tools/analyze_g2_tinyframe_send_version.py).

## Result

The G2 object/port delta can be isolated without modifying the authenticated
MIT TinyFrame sources. The candidate in
[`components/shared/tinyframe`](../../components/shared/tinyframe/runtime_tinyframe_g2_adapter_candidate.c)
allocates this target layout:

```text
allocation base   +0x0000  0xA5A5A5A5
pristine core     +0x0004  TinyFrame, 0x7158 bytes
suffix bookend    +0x715c  0x5A5A5A5A
allocation end    +0x7160
```

The adapter returns the pristine core pointer at allocation base `+4`. This is
safe only as an atomic source-routing design, not as a mixed stock/source ABI.
The stock census proves why: application code never dereferences an instance
field. Every retained use loads the one global pointer and passes it to a
public TinyFrame entry, while listener and timeout callbacks pass that same
opaque pointer back into `TF_Respond` or application callback code.

The upstream `TinyFrame.c` and `TinyFrame.h` remain byte-exact. During candidate
compilation only the three upstream lifecycle symbols are renamed:

```text
TF_Init       -> open_cfw_tinyframe_upstream_init
TF_InitStatic -> open_cfw_tinyframe_upstream_init_static
TF_DeInit     -> open_cfw_tinyframe_upstream_deinit
```

The G2 constructor calls the renamed pristine static initializer inside the
bookended allocation. `TF_WriteImpl` is a separate injected port which ignores
the instance pointer and forwards `(buffer, length, timeout=100)`, matching the
14-byte stock wrapper. `TF_Error` is isolated behind a `va_list` logging port;
it does not claim byte-exact EasyLogger formatting or stock source-line output.

The companion production-excluded port candidate
[`runtime_tinyframe_g2_production_ports_candidate.c`](../../components/shared/tinyframe/runtime_tinyframe_g2_production_ports_candidate.c)
now makes the two functional bindings concrete. Allocation and release use the
source-owned `heap_4` boundary. Writes retain the independently authenticated
first-party synchronous wrapper at `0x00541790`; they do not recreate its
hardware provider. The candidate intentionally installs a no-op logging port,
because logs are diagnostic policy and the retained vararg EasyLogger ABI is
not needed for TinyFrame wire behavior.

The further stateless atomic-boundary candidate
[`runtime_tinyframe_g2_atomic_boundary_candidate.c`](../../components/shared/tinyframe/runtime_tinyframe_g2_atomic_boundary_candidate.c)
removes the writable port table entirely. Its `TF_Init` allocates the exact
bookended object through source-owned `heap_4`, its `TF_WriteImpl` calls the
retained wrapper at Thumb entry `0x00541791`, and its local memory fill removes
the released DLIB ABI from the closure. The separate
[`../../third_party/tinyframe/g2-production/TF_Config.h`](../../third_party/tinyframe/g2-production/TF_Config.h)
inherits every recovered protocol/ABI setting and makes logging an explicit
no-op policy; the authenticated upstream files and recovered base config are
unchanged.

## Runtime instance and peer-role census

There is exactly one runtime TinyFrame instance pointer, stored at
`0x200749C4`. The 32-bit value appears in exactly two image literal pools,
`0x0045DD64` and `0x0045EBDC`. The complete direct-caller census and three
application-span hashes close all consumers:

| Source behavior | Stock evidence |
|---|---|
| periodic tick | pointer load at `0x0045D4BC`; `TF_Tick` call `0x0045D4C2` |
| receive ingress | pointer-slot load at `0x0045D4DE`; `TF_Accept` call `0x0045D530` |
| multipart begin/payload/close | calls `0x0045E76A`, `0x0045E808`, `0x0045E858` |
| type-listener registration | seven calls in `SyncModuleInit` |
| response building | twelve application `TF_Respond` calls |

`SyncModuleInit` is exactly bounded at `[0x0045E8D0,0x0045EB76)`, 678 bytes,
SHA-256 `62326c6a631f068f05f8141a8960aeab9a11242ab9f559507e9adf1b21e72360`.
Its role mapping is definitive:

| Sync role | Diagnostic | Constructor argument | Wire request-ID half |
|---:|---|---:|---|
| `1` | `Sync module start up as Master` | `TF_MASTER` / peer bit `1` | `0x8000..0xFFFF` |
| `2` | `Sync module start up as Slave` | `TF_SLAVE` / peer bit `0` | `0x0000..0x7FFF` |
| other | `unknown role,init failed...` | no instance | none |

The two role branches are mutually exclusive and store into the same global
slot, so this is one mode-selected instance, not two concurrent instances.

## Candidate verification

The host oracle compiles the exact upstream core, adapter, and port fixture as
separate translation units and links them together. It verifies:

- allocation/core separation and both bookends;
- exact slave/master wire frames from the upstream core;
- the stock transport timeout `100`;
- receive-listener and timeout-callback pointer identity;
- log-port delivery on checksum error and listener expiry; and
- bookend survival after receive/send activity.

A separate Cortex-M55 compile enables `-fshort-enums` and evaluates target-only
static assertions for core size `0x7158`, core offset `+4`, suffix offset
`+0x715C`, and allocation size `0x7160`.

The concrete-port fixture additionally proves the exact `0x7160` heap request,
release pointer, unchanged transport buffer/length/timeout arguments, and
configuration-before-initialization order. Its Cortex-M55 object pins all five
code sections, the 20-byte port table, and every relocation. The retained
transport evidence is:

| Boundary | Stock span | SHA-256 | Result |
|---|---:|---|---|
| synchronous write wrapper | `[0x00541790,0x005417A4)` | `f9ba82957a18e3ae966a6f8b6af0d7160d2ba237a61024b98cd5c938b8734d67` | two direct callers only: TinyFrame and first-party handshake; maps provider success to `0`, all failures to `-1` |
| hardware-facing provider | `[0x00584C98,0x00584DB6)` | `0a13941f278f566dff230b8fea27c85b231070ed2109d5b490ef48aa1943d18c` | retained opaque provider; receives `(buffer,length,timeout)` unchanged |

The atomic target compile starts from the eight stock-facing roots `TF_Init`,
`TF_AddTypeListener`, `TF_Accept`, `TF_Respond`, `TF_Query_Multipart`,
`TF_Multipart_Payload`, `TF_Multipart_Close`, and `TF_Tick`. Reachability closes
at exactly fourteen live function sections with production logging disabled:
those roots, upstream
`TF_AcceptChar`/`TF_HandleReceivedMessage`/`TF_SendFrame`/renamed
`TF_InitStatic`, plus the local write and memory-fill functions. No writable
data and no live unresolved symbol remain. The only undefined symbols outside
that live set are source-owned heap allocation/free and the dead upstream
dynamic constructor's libc `malloc/free` references. Apple Clang produces
3,390 live code bytes (contract SHA-256 `0403dffc…b353a`); independent Linux
Clang 22.1.8 produces 3,466 bytes (`a61c4395…17e4f`). Both fail closed on the
complete section/relocation graph.

```sh
python3 -m unittest -v tests.test_tinyframe_g2_adapter_candidate
python3 -m unittest -v tests.test_tinyframe_g2_production_ports_candidate
python3 -m unittest -v tests.test_tinyframe_g2_atomic_boundary_candidate
python3 -m unittest -v tests.test_analyze_g2_tinyframe_send_version
python3 tools/analyze_g2_tinyframe_send_version.py
```

## Atomic production routing and remaining validation

Production redirects the complete stock entries for
`TF_Init`, `TF_AddTypeListener`, `TF_Accept`, `TF_Respond`,
`TF_Query_Multipart`, `TF_Multipart_Payload`, `TF_Multipart_Close`, and
`TF_Tick` together. The source core's private call closure and `TF_WriteImpl`
are linked in the same promotion. Routing only a subset would mix the
vendor-base and pristine-core pointer conventions and is rejected.

The promoted Apple-Clang overlay is 142,310 bytes with SHA-256
`1fd5f8940b18341f2812669e99890be6b3445eb09fa24b88e0d8058a5a4f8264`;
the complete Apollo-main component is 3,665,706 bytes with SHA-256
`1ed36ee81df0b3a9ec0d74bcfddc38cc885e947a2f60b40a31eddd016c5b89cb`.
Linux Clang 22.1.8 independently produces a 144,266-byte overlay
(`4c95f20608c70a065b05837415d2d4471fc7eeeb61fa30ce1c1c9f07f717ddb9`)
and 3,667,662-byte component
(`686ea217db2837bffd8a190485f0a6f719242e927fba17281c6f54aa066767f6`).
The Apple package accounts for 142,977 source bytes, 98,824 generated bytes,
and 4,202,399 retained opaque/cut-forward bytes.

The only remaining TinyFrame functional validation is hardware golden frames
for both master and slave roles, including multipart and timeout behavior.

The peer-role census, G2 bookended layout, heap binding, and retained transport
boundary are closed. Placement, redirects, ownership accounting, the explicit
no-op logging policy, and the exact live atomic source graph are dual-profile
pinned. Exact historical checkout selection inside the source-identical
`eb75483e…a29167a` interval remains binary-unobservable, not a functional gap.
