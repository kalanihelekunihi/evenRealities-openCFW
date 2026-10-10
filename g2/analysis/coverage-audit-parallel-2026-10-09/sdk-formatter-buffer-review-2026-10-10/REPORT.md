# Independent SDK formatter buffer review

PASS for finite expected-output/guard test suite; FAIL for arbitrary internal-buffer safety. Independently rebuilt/replayed all116child runs:108ordinary cases pass;8internal probes retain four fatal sanitizer diagnostics. Exact ordinary stdout matches all108owner receipts and stderr is empty. Source/header/compiler identities and aggregate verification match; checks.json records independent checks. Owner sources/seals remain read-only; all audit output isolated. No stock target execution, denied discovery/acquisition/provider phase, exploitation, fix or coverage promotion.

## Public API behavior verified

Unchanged SDK5.2 am_util_stdio_vsnprintf rejects n>=1024 before touching format. Otherwise it first formats into global g_prfbuf, then returns0 if formatted length>=n; on success it copies only formatted-length bytes and returns that length. No destination NUL is copied. am_util_stdio_snprintf forwards real va_list; both entrypoints tested. This is not ISO snprintf semantics. Header parameter comment labels n 'number of arguments', which is misleading relative to implementation; actual source and observed capacity behavior govern this bounded finding.

Expected text is independently specified in harness, including decimal/hex/signed/width/string/char/percent and ±1.25float cases. Guard-page allocation places declared capacity immediately before PROT_NONE; accessible page initializedA7 and everybyte checked. Accepted output lacks terminator with next byteA7; equal/insufficient capacity returns0 preserving destination. n0 and invalid format early-return cases are explicit projections, not valid production caller examples.1022/1023boundary cases bracket internal1024 versus destination acceptance. Return0 is ambiguous for empty output/rejection.

## Safety failures and instrumentation caveat

Plain1024byte global configuration reports ASan global-buffer-overflow for1024chars+n1,1024chars+n0,2049chars+n1 (three fatal processes). These are observed failures, not passed safety tests. Output n0 does not suppress preceding internal formatting.

AM_PART_APOLLO5_API doubles/aligned global to2048bytes.1024char controls fit;2049chars exceed declared object but default ASan produces no fatal diagnostic. This nonfatal result is not safety evidence. Test-only single-TU inclusion exposes unchanged private buffer and poisons64shadow bytes after its exact end;1024control succeeds,2049 produces fatal use-after-poison. Its instrumentation differs from separate-source build, so label the fourth diagnostic distinctly rather than claiming four identical default-ASan global-overflows. Root cause of default aligned-global sanitizer omission remains unresolved.

Destination whole-page checks detect lasting changes and protected-page violations, not writes later restored or all internal globals/threads. Source sanitizers and guarded controls provide finite memory evidence; arbitrary formats, signed minima/all floats/widths, reentrancy/locking and callback delivery remain outside tested scope. Explicit poison affects sanitizer shadow instrumentation, not formatter body or production declaration, and supplies no stock behavior claim.

## G2 applicability boundary

All execution is native macOS arm64 Appleclang21O1 with native va_list/system headers and ASan/UBSan; neither ARM candidate ELF nor locked G2 firmware is executed. Both macro configurations are deliberate candidates, not recovered stock. Stock uses IAR/runtime/application logger bindings; the previous zero-undefined SDK link did not bind TLSF printf/memcpy/assert names. Before G2 applicability, independently bind stock callsites/body/config/buffer placement and length contracts to this exact implementation, then test authentic target ABI/runtime initialization and source-owned logger/callback integration. Physical console/MMIO/interrupt/cache/concurrency behavior remains separate. These findings must not be presented as a G2 vulnerability or a fix requirement without that binding.

Finite requested buffer experiment is complete with the stated PASS/FAIL distinction. No further overflow probing is needed for this scope. Keep preserved fatal and sanitizer-blind receipts; no arbitrary-input safe claim follows. No complete source build, source-compilable percentage, stock byte equality or canonical admission changes.

Artifacts: checks.json, verification.json, replay scripts/harnesses, compile records and all116child stdout/stderr. Owner report: g2/analysis/sdk-formatter-buffer-20261010-implementation/REPORT.md.
