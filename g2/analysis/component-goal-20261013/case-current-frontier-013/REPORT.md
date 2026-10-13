# CASE current frontier: matching, custom image, hardware

The reproducible401-unit CASE source profile remains63,122bytes,7,370bytes above the locked55,752-byte payload. Its reset-to-application boundary, selectedABI, RAM-state, interrupt andGPIO domains are qualified;0/6 replacement images are accepted.

Exact binary matching is constrained by TC-ARMCLANG6 and the absent authenticated compiler release, per-file flags and scatter/project recipe. No armclang/armlink executable was discovered in the inspected environment. This constrains reproduction of the official bytes; it does not prove source-level size or behavior improvements exhausted.

A runnable custom image has a different capacity question. The consolidated native memory evidence documents an active256KiB bank and preserved device-data slots near0x0803F000/0x0803F800. The current63,122-byte load span is well below the first reserved page. Thus the7,370-byte stock-length overage is not an established physical-capacity failure. A custom-image constrained linker/package still needs explicit protected-region andRAM contracts, complete providers/computed-root/ambient-stack evidence, and runtime validation. It is not yet firmware-ready merely because the image fits.

Hardware acceptance remains separate: physical clock startup, IRQ/FIFO timing, scheduler arbitration, GPIO output and flash persistence are unvalidated, and no flashing approval exists. These gates do not prevent additional justified software work.

| Investigated candidate | Evidence and present decision |
|---|---|
| Frame record router08001E94:RAM-only command/state/chunk paths | Supported now. Actual source/providers and locked nativebody exist; older test covered50selected cases with isolated oracle setup. Continue full linked native/C tests across commandfamilies, packet/header positions, charging-state branches and chunk lengths. Diagnose/fix concrete mismatches. Forwarding/logging I/O must be qualified separately; do not fabricate returns. |
| Custom-image memory-constrained build | Supported next. Current image fits below documented preserved pages. Add source-derived linker assertions, bounds and reproducibleartifact; does not require originalcompiler just to establish a custombuild contract. Hardware/readiness remains open. |
| Battery measurement9EBC shared typed ABI | Supported lower-priority candidate. Two equivalent providers and one void-return caller conflict with selectedint32provider ABI. Existing query/divide cuts are available, but physical sensor effects not validated. This is not blocked by originalcompiler; prioritize broader router behavior first. |
| More open-compiler outlining/function-merge/profile flags | Tested scoped options either unchanged, larger, ABI-failing or admitted; do not infer universal exhaustion or perform unmotivated versionlotteries. |
| Exact stock compiler/project matching | Cannot presently close: producingtools and authenticatedrecipe missing. Existing local compilerfingerprint/recipe-boundary evidence pinned. |
| Touch generated widget/history providers | Still blocked: nonzero widgethalfword142 lacks authenticated generator/consumer meaning;426byteRAMgap does not prove history capacity. No invented padding/count. |
| Switch to boot/EM/codecs | Not selected while supportedCASE work remains. MAIN/FreeType stays existingowner's scope; any later component switch requires ranking and ownership agreement. |

This frontier supersedes any reading of frontier012 as a universal software-exhaustion claim. Keep frontier012 historically intact. No Goal/scheduler control is a substantive stopcondition, and no additional scheduler will be attempted. Source checkpoints and compiledsymbol envelopes remain separate from native-byte coverage; historical mapcutoff2026-10-13T17:02:21.929738Z remains unchanged.
