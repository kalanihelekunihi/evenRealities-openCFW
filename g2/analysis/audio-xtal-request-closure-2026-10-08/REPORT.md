# Native XTAL request/wait, board initialization and HFRC configuration

Five complete native offline functions pass **836 original-instruction comparisons on one final artifact**:404 XTAL/request/wait/board fixtures and432 HFRC config fixtures. **12 original-only assertions** execute the platform board-copy/set block and subsequent XTAL request. [Reconstructed source](../../components/audio/xtal_request_offline/request.c), [interfaces/layout](../../components/audio/xtal_request_offline/request.h), [exact validation](exact-build-validation.json), [addresses/hashes/disassembly](function-bindings.json). ELF SHA256 `dadddc179d3c595cf782166eced5130bfc2989e00c172c7f2c545f90e1511e2d`.

## Correction and stock board defaults

The previous sealed ownership report called0x4C38A0 a board-info initialization lead. **That identification was incorrect: it is HFRC configuration.** This additive report corrects it without changing the prior seal. Actual board setter0x4C45E2 copies20 bytes to0x200001CC and rejects NULL with6. It does not validate mode/frequency or mask padding. Current public SDK adds a SIP bool beyond this stock layout; copying the SDK structure size would overwrite adjacent state.

Platform block0x4C2B06..0x4C2B18 copies20 bytes from main-image table0x77D8F8 and calls that setter. Values are XTAL-HS mode0/frequency0; XTAL-LS mode0/frequency32768; external reference12000000. The tests preserve the following four sentinel bytes. They stop before subsequent HFRC/HFRC2 calls; they do not prove complete platform initialization or that later callers never replace board info.

**After these defaults are installed, XTAL request returns7 without acquiring a user.** The previous invalid-drive ownership retention requires a nonzero XTAL-HS configuration, as explicitly supplied by those synthetic24MHz fixtures. It is not established for stock startup defaults. No connected device configuration was observed.

## XTAL request ownership and timeout

Native request0x4C3D9E, XTAL wait0x4C3D70 and counter wait0x4C387E preserve the stock flows. Missing configured frequency returns7 before IRQ/user state. Already-owned user skips mode conflict checks, copies an active shared counter if present, publishes its own stack counter pointer unconditionally, then waits. New requests inspect external/crystal enable bits, start the selected oscillator when off, return3 for known mode conflicts, and set ownership only when status0. Board mode values other than0/1 follow the exact stock comparisons; no sanitization is added.

The child assumes a validated byte user. Direct invalid-user fixtures document its missing validation; public request dispatch guards users<57. Do not expose the child as an arbitrary-input app API.

Counter wait repeatedly calls actual delay API(10) and decrements until zero or flag clear. XTAL wait then clears flag/pointer under saved IRQ mask. There is **no hardware-ready poll and no timeout error**: counter exhaustion returns success. Tests include counter0/1/3/150, initial IRQ masks, and synthetic flag clears at selected delay entries. These are synchronous emulator changes, not IRQ scheduling evidence. Pinned source identifies microsecond API units; elapsed physical time remains unproved. When stabilization was already false, wait skips cleanup, preserving the earlier proven inactive stack-pointer state.

## Corrected HFRC source lead

Native0x4C38A0 accepts only frequency0 (free-running approximately48MHz) or48000000 (adjusted); other values return5. Adjusted mode requires nonzero XTAL-LS frequency even with explicit config, else7. Generated target is integer requested/reference inserted into bits8..19 of default packed0x0025B800, truncating to12 bits. Explicit configs copy all12 bytes.

With active clock4 users, reconfiguration is permitted only when cached frequency is0 or48000000; otherwise3 and cache unchanged. Allowed active transitions immediately apply/disable HFADJ. Without active users, changing selected frequency disables HFADJ and clears stabilization, then stores configuration for a later request. Configuration-valid byte0x20004536 therefore does not prove adjustment enabled or physical frequency. Selected frequency0x20074250, packed cache0x20073F30 and stabilization flag/pointer0x20074F57/0x20074264 are separately recovered.

Actual target/apply/disable providers execute; stock apply and nonzero-reference target return0. The rollback/nonzero-provider-status branches are preserved statically but cannot be dynamically forced with those actual providers; no error-return stub is used.

## Limits, preservation and next leads

Original oscillator, delay, IRQ-save and HFRC providers remain explicit dependencies. Local stack-pointer addresses are normalized; frame layout and void-return scratch registers are excluded. Board memcpy overlap behavior is not tested. Synthetic MMIO/configuration does not establish physical readiness, IRQ concurrency or real reference availability.

Prior seals,110 inputs,four checkpoint images match; concurrent staging was inspected read-only and preserved. No commits, production changes or device writes. The next concrete pinned-source leads remain HFRC/HFRC2 request/release and configuration, SYSPLL reference switching and manager dispatch/integration. Available leads are not exhausted; missing physical/IRQ evidence is a boundary for hardware/concurrency claims, not a reason to abandon source closure.
