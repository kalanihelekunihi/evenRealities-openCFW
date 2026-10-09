# Native low-speed ownership and public clock dispatch

Six new native functions pass **1,584 original-instruction comparisons**. The same final combined ELF passes **3,403 reused composition cases** (1,144 config,1,407 driver,816 manager,36 stock configuration/request/repeat/release). Total4,987 is an artifact regression count, not distinct firmware coverage. ELF SHA256 `30f73066f0de99e83084a84921d9e32d93dfac369cc79c551f9ae11aa7daaf47`. [Readable C](../../components/audio/clock_public_dispatch_offline/dispatch.c), [interface](../../components/audio/clock_public_dispatch_offline/dispatch.h), [pseudocode](pseudocode.md), [exact validation](exact-build-validation.json), [addresses/code hashes](function-bindings.json).

## Low-speed ownership is not hardware readiness

LFRC request0x4C3BFC/release0x4C3C2E use clock0 bitmap. XTAL-LS request0x4C3C60/release0x4C3CA2 use clock1. Requests are idempotent ownership bits, not counted references. A new set/clear occurs under saved PRIMASK through actual IRQ helper; repeat request or absent-user release skips it. Children discard user-set return; public entry guards the byte user first.

XTAL-LS request reads configured LS Hz at0x200001D8 **before querying existing ownership**. Thus configured0 returns7 even with an already-set user bit; release can still clear that bit and return0. Source SDK optionally enables, checks and disables EXT32K, but those conditional hardware bodies are absent from stock functions. Tests vary LS mode0/1/255 and configured0/32768; no mode-specific MMIO change occurs. Success is ownership bookkeeping, not proof a32768Hz oscillator is running. LFRC ignores board frequency entirely.

## Public dispatch ABI

Request0x4C44BC/release0x4C4530 narrow both clock/user to uint8. User>=57 after narrowing returns6 before entering any child. Clock0..6 maps LFRC,XTAL-LS,XTAL-HS,external,HFRC,HFRC2,SYSPLL; unknown clock returns6. Full-width256 wraps to0,312 wraps to56; this is stock ABI, not an input-safety recommendation. App/CFW adapters should validate full-width values before calling. Releases remain idempotent and inherit each child’s cleanup/error semantics.

Direct fixtures compare ordered bitmap/MMIO writes, child call names/arguments, delays, flags/handle/driver state, fullFPSCR and PRIMASK. They cover valid/wrapped/invalid clock/users, repeat/existing-other ownership, configured missing references and stock defaults. Local inactive counter-pointer addresses are normalized; their scheduling/lifetime is not proven. Selected ready/lock bits are explicitly synthetic; no actual hardware timing or BLE/app call route is established.

## Existing oscillator integration

Previously sealed native oscillator0x4809C4 is now compiled unchanged into this combined artifact. Its clock2/user52 request/release now resolves to native public dispatch and existing native XTAL children, so normal32M source differences, CLKOUT acquire-before-drive-validation and last-user release behavior are carried through the actual native call chain. No prior source/seal was edited. Synthetic nonzeroHS cases remain separate from stock boardHS0.

SYSPLL generator still preserves finite limits,NaN behavior and min-VCO partial writes from its prior sealed batch. Four original math-runtime providers and delay/status/IRQ helpers remain explicit original dependencies in this artifact, not stubs. Their source-backed assessment proceeds separately: floor/round/ceil are small integer bit cores; fmod has normalized integer remainder and domain-error/errno handling. The pinned SDK calls them but does not contain their implementation. No unique runtime vendor/version or global source-exhaustion claim is made.

All prior inspected seals,110 inputs,four checkpoints and staging were preserved. Only these owned additive directories were written. No shared gate/production changes, commits or device writes. [Preservation](preservation.json).
