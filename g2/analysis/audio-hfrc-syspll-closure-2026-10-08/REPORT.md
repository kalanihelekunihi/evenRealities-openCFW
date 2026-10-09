# HFRC/HFRC2 ownership and SYSPLL integration

Eight complete native request/release/wait functions pass **848 original-instruction comparisons** against one final ELF:816 direct/state cases and32 repeated request/release sequences. **Eight original-only configuration guard assertions** distinguish stock-compatible references from manually seeded invalid caches. [Readable C](../../components/audio/hfrc_syspll_offline/clocks.c), [interfaces](../../components/audio/hfrc_syspll_offline/clocks.h), [exact build](exact-build-validation.json), [body/data addresses and hashes](function-bindings.json). ELF SHA256 `377180ccdaabb0d6747209658903661286f1442c0d1d2d22fb4695011623eed0`.

## Stock board reachability

Stock platform defaults remain HS frequency0,LS32768,external12000000. Both actual HFRC2 and SYSPLL configuration functions reject explicit XTAL-reference configurations with7 when HS frequency is zero, and leave config-valid false. External-reference configurations in the same no-active-user fixtures succeed. Separate HS24MHz tests are explicitly synthetic; no running board was observed.

Tests manually seeding valid adjusted XTAL-reference cache at HS=0 exercise error preservation but **are not established stock-startup paths**. Such state requires a changed cache/board history. Likewise an existing-other-user fixture without a corresponding handle tests branches, not reachable startup state. The raw board setter can change board info without validation, but no live caller sequence is inferred.

## HFRC request/release

Clock4 ownership is a user bitmap. First valid user sets force-on bit0 at0x40004044. Adjusted configuration applies cached HFADJ; new stabilization uses1000 software delay iterations. Wait completion sets0x20074F59 (software stabilized), clears flag/pointer and does not read hardware-ready status. Invalid cached config returns1 without ownership. Already-owned users bypass config validation and can preserve an inactive pointer to a returned local counter, as with XTAL.

Last-user release clears only force-on. **Stock does not disable HFADJ or clear stabilization/stabilized state**, unlike the extra controlled path in pinned SDK. Native/original request-repeat-release sequences prove HFADJ bit0 stays set and stabilized remains1 after adjusted last-user release while force bit0 clears. This does not prove a physical clock stops or continues.

## HFRC2 dependency and overwritten failure

Clock5 request publishes its user bit and, for the first user, start-pending before acquiring a reference. Adjusted mode uses dependency user54: XTAL when reference byte0, external otherwise. Dependency failure removes caller ownership. However, cleanup assigns the reference **release return into the status variable**, overwriting the original error. In manually seeded valid adjusted XTAL cache with HS=0, actual XTAL request returns7, release returns0, and HFRC2 request returns0 with caller bit clear and start-pending still1. The configuration guard above prevents calling this an ordinary stock-default configuration.

Valid external/free-run branches execute actual force/apply providers. Force-on provider status is discarded. Invalid config returns1 and removes caller ownership; its pending marker can remain. Software wait has50 initial iterations and no hardware-ready check. Last-user adjusted release disables HF2ADJ, releases both possible dependency clocks, clears pending/flag/pointer and clears force bit5. Free-run release clears force only; flags/pending may survive.

## SYSPLL selected-reference status and lock ownership

Clock6 request publishes ownership/pending before dependencies. It requests both references with dependency user53; only selected-reference return controls progress. Thus external selected + HS=0 can continue despite the ignored XTAL7. It initializes/configures/enables a real stock driver handle, releases the nonselected source, then calls actual lock wait. Setup failure removes caller ownership, deinitializes a nonNULL handle and releases both references; driver/provider errors are not stubbed.

**Lock-wait failure happens after setup cleanup decisions.** Under explicit synthetic power-ready bits and external reference, lockbit0 makes actual poll return4 while caller ownership, selected external reference and initialized/enabled handle remain. A second request returns0 immediately because the caller bit is already present; it does not recheck lock. Explicit release clears ownership, disables/deinitializes and nulls the handle for the last user. Tests record the exact sequence4→0→0 and final cleanup. This is software state demonstrated offline, not a hardware incident or proven simulator timing model.

SYSPLL release discards driver disable/deinitialize/reference-release statuses. Selected reference is released only on last user. Configuration parameter errors6 and power-not-ready7 are actual original provider paths; setup cleanup differs from late lock timeout. [Direct results](results.json), [sequences](sequence-results.json), [stock configuration guards](config-constraint-results.json).

## Validation limits and actionable leads

Native XTAL and bitmap helpers are reused unchanged. Original GPIO/external reference, oscillator, delay, IRQ-save and SYSPLL/HFRC driver bodies execute. Original wait routines see synthetic power/lock/status fields; stabilization flag clear at a selected delay entry is synchronous synthetic input, not IRQ concurrency. Counter expiry success, software stabilized flags and retained clock requests are never treated as physical readiness. Local counter-pointer addresses are normalized; scratch frames/void-return registers excluded.

Further available pinned-source leads are native external-reference request/release and manager dispatch, HFRC2/SYSPLL configuration closure, and native driver initialize/configure/enable/lock/cleanup. Board-info lead correction remains in the [index](INDEX.md). Source leads are not exhausted. Real hardware readiness/reference availability and IRQ scheduling require external evidence.

Prior seals,110 inputs,four checkpoints and concurrent staging are preserved. No commits, production edits, device writes or shared campaign changes.
