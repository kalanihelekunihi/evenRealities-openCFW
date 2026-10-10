# Final registered-source boundary pass

Status: partial, pending independent review. This closes the requested *bounded dependency-identification pass*, not firmware pseudocode, G2 source completeness, or byte equality. No canonical ledger, gate, firmware source, installed processor, or shared GUI project was modified.

## Authentication and scope

Eight minimal bodies, 210 instruction bytes, were exported using the private corrected C-SKY processor and independent GNU objdump. `bodies.json` records half-open runtime/child/codec spans and hashes. The authenticated XIP child SHA-256 is `49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584`; runtime base `0x10203004` remains the reviewed conditional XIP mapping, not observed hardware placement. Prior passes authenticate its relation to the locked bundle and codec. `run.py` rechecks the child hash before analysis.

Public source: registered `third-party/upstream/nationalchip-lvp-kws`, commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`. Public driver archive: `lib/libdriver_release_v1.0.6.a`. No new source download is justified by this pass: the positive source matches are already registered; driver C implementations are not exposed by those public headers or archive objects.

## Positive source constraints

| Entry | Bytes | Source-backed constraint |
|---|---:|---|
| `10206d90` |24| `LvpKwsInit`: unsigned start mode below 2 invokes model loader `10206cb0`, then SNPU init `10205cf4`; saves supplied callback; returns 0. Public `lvp/common/snpu_engine/lvp_kws.c:484` has this skeleton. Config-dependent cascade/hybrid branches are absent in this body. |
| `10206dac` |14| `LvpKwsDone`: SNPU exit `10205d40`, callback cleared, r0=0. Raw C signature from decompiler is void; native r0 assignment and public source establish returned zero. |
| `102073f8` |10| `LvpAudioInDone`: audio exit `10204984`, returns 0, public `lvp/common/lvp_audio_in.c:620`. |
| `10207660` |28| `LvpAudioInStandbyToStartup`: replace upper nibble of byte `2002ecb0+0x10` with 1, preserving lower nibble; call interrupt-enable `102047b8` with mask `0x30007`, enable=1. Public bitfield `standby_startup_flag:4` and PCM0/PCM1/LOGFBANK/FFTVAD start/finish mask agree. Native listing proves r1=1 although untyped decompiler omits that argument. |
| `10207680` |54| `LvpPmuInit`: wake source<2 clears 0x90 bytes of handle and returns1; otherwise iterates registered resume count and invokes callback(priv), returns0. Source `lvp/common/lvp_pmu.c:40` agrees. Callback targets/count are mutable retained-state input, not closed by public source. |
| `10208944` |22| `LvpInitMaxKws`: compare count at pointed structure+0x58 against2; conditional error print, then strategy-init candidate `10208978`. Public `lvp/vui/kws/max_decoder.c:193` constrains intent; source alone does not prove model/list payload contents or strategy transitive semantics. |

Other public providers discovered without needless body export: `LvpInitBuffer` has configuration-dependent construction in `lvp/common/lvp_buffer.c:95`; `LvpAudioInInit` constructs callback configuration then calls `gx_audio_in_init`, in `lvp/common/lvp_audio_in.c:597`; decoder implementation is in `lvp/vui/kws/max_decoder.c:174`. Their source is usable for later first-party P2 inference, but parsing all those bodies now would be a new semantic reconstruction frontier rather than finding new dependency sources.

## Minimal archive provenance tests

`providers.py`, `archive-matches.json`, extracted objects and native archive listings preserve reproducible symbol evidence.

- `gx_audio_in_set_interrupt_enable` at `102047b8`: full 42-byte section **exact**, no relocations. For enable!=0 it writes mask to `a0a00104`, then reads `a0a00100`, ORs mask, writes enable word; disable reverses order (clear enable mask then write clear/status mask). Returns0. MMIO ordering is observable and must be preserved.
- `gx_audio_in_exit` at `10204984`: 42-byte section equal outside five explicitly named BSR relocations (`_ain_reset`, four `gx_clock_set_module_enable` calls). This identifies the provider, but does not independently prove every linked callee implementation.
- `gx_snpu_exit` at `10205d40`: 32-byte archive `.sram_text` slice at offset `0x448` equals outside four named BSR relocations. Names expose IRQ12 mask/unmask, suspend, conditional device exit. The firmware places this code in the XIP child despite archive section naming; section name is not physical placement proof.
- `gx_snpu_init` at `10205cf4`: 64-byte archive slice at `0x408` is **not** strict relocation-only equality: remaining differences are decimal offsets2/3,30/31,50/51, all three LRW pool-offset encodings. Native listings show identical operations and correspondingly moved literals: state pointer, `a0c00190`, request-IRQ callback. This is a strong source/archive identification, not an exact byte match. The differences are literal-pool layout, not evidence of a changed algorithm. No additional bytes were silently excluded.

These archives constrain private HAL behavior but are executable evidence, not permissible retained implementation for the final from-source target. SNPU device/tcb/IRQ internals and audio reset/config remain provider boundaries unless separately reviewed. This pass does not assert that every private archive symbol has been exhaustively analyzed.

## Firmware-specific app boundary

Previous pass identified app callbacks with substantially more behavior than public `app/sample/lvp_app_sample.c`: stateful initialization, event91 packet construction, event100/101 helper calls, and nonempty task loop. Public sample's task loop returns0, suspend/resume merely print, and its nonfactory event handler only reads context and prints. `app/iic_test/lvp_iic_test.c` was also checked: its I2C demo and delay/counter loop are not those shipped paths. Shared sample names/strings establish scaffolding ancestry, not app implementation equivalence.

Only two new app helpers were needed:

- `1020975c` (20 bytes): invokes `102093dc`, then calls `102093f4(1,12,event_argument)`. Public sample does not define this event packaging behavior. Protocol meaning and downstream effects remain unassigned.
- `10209770` (38 bytes): constructs a request in a global structure, stores pointer to local byte1 at offset0x10, halfword0x10f at+4, byte1 at+7, word1 at+0x18, then calls `102083bc`. This proves a firmware-specific request shape, not the lifetime/synchronous-copy safety of its stack pointer or the identity of its consumer. Do not name it as a hardware command without downstream proof.

Remaining custom family `{102096fc,1020979c,102097c8,10208ff0,1020913c,10208e80}` and downstream `{102093dc,102093f4,102083bc}` is a first-party semantic frontier. The registered public sample is insufficient to replace it. No negative claim that these byte sequences cannot exist in any third-party repository is made.

## Stop boundary and outstanding work

The requested final dependency-source boundary has been reached: public lifecycle code and named archive provider identities have been established; the unresolved app request/event behavior needs actual firmware-semantic review, while private HAL source remains unavailable in this registered provider. Continuing transitive decompilation would expand beyond the requested bounded source-identification pass. No material tool failures in the eight exports; all decompiles completed. Known decompiler signature loss was explicitly corrected using native evidence. Previous shared Ghidra-MCP GUI remains intentionally untouched.

New bytes this pass210; prior three passes2672; total scoped body bytes2882, **not accepted coverage**. Do not add archive section sizes to pseudocode body coverage. Independent review, retained-state dispatch, transitive callee effects, hardware delivery/mapping, model payloads, full corpus freeze, implementation and byte comparison remain distinct outstanding gates.
