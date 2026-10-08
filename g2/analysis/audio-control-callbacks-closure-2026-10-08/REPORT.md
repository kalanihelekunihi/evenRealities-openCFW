# Queued type0/type1 controls and producer-stop prefixes

**576 PASS original/independent dispatch comparisons**, using the authenticated eight-row table at **0x20003FBC**. Original0x53C5AC enters type0 callback0x53C860 or type1 callback0x53C7B0; independent source reconstructs their routing and selected I2S/PDM stop prefixes. Actual role getter/NVIC-disable/null-watchdog peers execute; downstream providers stop before their first instruction. [C source](../../components/audio/control_callbacks_offline/control.c), [results](results.json), [instructions](original-disassembly.txt).

## Message and routing

Selected message is12 bytes: u32 type+0,mode+4,value+8. Dispatch compares low16 type; callbacks use **low8 value**. Values256 alias0;258 alias2. Callback behavior does not read mode+4 here. Synthetic upper type bits0x10000 still select the same callback; this is not proof such a message is produced by valid firmware callers.

Role getter0x4ABE60 reads byte0x200038F1. Type0 uses role==1 versus other roles. Type1 selects primary PDM only if role==1 and variant byte0x20075019 is0; otherwise alternate PDM. Role/variant meanings beyond this route are not established by these tests.

| Callback | Selected behavior |
| --- | --- |
| Type0, role1 | Nonzero low value enters DSP enable0x57D6B4; zero enters DSP disable0x57D794. Later gate/I2S calls are static continuations, not executed after the first boundary. |
| Type0, other role, value2 | First calls special control0x57A816(0); stops there. Later enable flow is not executed. |
| Type0, other role, other nonzero | Sets byte0x2007502E=1 and counter0x20074A9C=0, then reaches DSP-enable boundary. |
| Type0, other role, value0 | Clears those state fields, invokes actual watchdog-stop with NULL timer, then I2S stop. Inactive I2S returns and reaches delay50 **ticks**; active I2S follows NVIC/clock prefix below. |
| Type1, nonzero | Primary enable0x57B4A8 or alternate enable0x57B770 entry boundary. |
| Type1, zero | Inactive channel returns. Active channel clears its active marker and reaches PDM interrupt-clear0x5925B4(handle,0x18). No peripheral interpretation or completion is asserted beyond that boundary. |

## Stop ordering: software state is not a DMA fence

Original I2S stop0x57A734 checks byte0x20074FB7. If active, **clears this marker first**, disables IRQ44 through actual0x57A48A, then calls clock-stop0x4C3138(0,0). Verifier checks NVIC ICER write **0xE000E184=0x1000**, derived from authenticated IRQ word0x78F558=44. It stops before clock-stop entry. Later power-control0x590648(handle,1,0), DMA-stop0x590C62 and uninitialize0x5900CE are static continuations only. No pending interrupt clearing, in-flight DMA completion or actual interrupt masking effect is simulated by passive MMIO.

Primary PDM active byte0x20074FBB/handle0x20074550; alternate active byte0x20074FBA/handle0x2007454C. Each clears its marker before the first interrupt-clear call. A zero marker therefore cannot be treated as proof every later hardware operation has finished. Source includes a deliberately bounded PDM prefix, not the remaining stop implementation.

Inputs: types0/1, roles0/1/2, variant0/1, six values0/1/2/256/258/FFFFFFFF, I2S/PDM active0/1, upper type bits0/10000. Logging0; watchdogNULL; constructed handles. No actual queue drain, live scheduling, board role or invalid-pointer safety is claimed. DSP/start/special/delay/clock/PDM-clear calls are entry boundaries, never executable fake returns. Tick units are retained without milliseconds claims.

## Lifecycle connection

[Stop handshake](../audio-stop-handshake-closure-2026-10-08/REPORT.md) remains corrected: request is thread flag0x800000; event8 is the **early acknowledgment before cleanup**. A queued type0/type1 disable requires dispatcher consumption and later providers; the acknowledgment alone establishes none of those completions. [Diagnostic deinit](../audio-diagnostic-deinit-closure-2026-10-08/REPORT.md) now tests publication and ownership gating separately.

Build_offline.py then opencfw venv verify.py. No production/index/commit/device changes; all prior967 seals,110 audit inputs and four checkpoints preserved. Next source leads: clock/power/DMA providers, DSP disable, variant-specific PDM interrupt/DMA cleanup, and their caller ordering. Physical stop completion requires peripheral/live ISR evidence; available code is not exhausted.
