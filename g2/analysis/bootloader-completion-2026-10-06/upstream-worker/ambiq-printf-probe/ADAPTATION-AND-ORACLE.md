# String candidate and FP64 oracle follow-through

`ambiq_stdio_string_candidate.c` retains the full downloaded Ambiq copyright/BSD-3-Clause notice and unchanged source provenance. Only its string branch and explicit-string-precision bookkeeping are adapted; integer/sink/float implementation remains the SDK implementation. The SDK original and failed comparisons remain preserved.

648/648 original-instruction boundary comparisons PASS (`string-boundaries.json`):9 width forms ×6 precision forms ×6 strings ×2 translation states. Tests include empty strings, width smaller/larger than content, zero-padding, negative widths, precision0/negative/short/long and strings longer than the SDK default precision. Negative controls are the retained original SDK failures on the same string contracts, not manufactured expected outputs. This is a host-compiled source candidate, not a target build or safe-overflow guarantee.

The M4/M7/M33 Unicorn models all reject original `vcvt.f32.f64` at0x415f52. Existing Cortex-A9 and A15 models execute it. Native host C conversion validates their result bits on2,007 seeded/edge binary64 inputs each, including signed zero, infinities, overflow and rounding-boundary fixtures. Default round-nearest, FZ/DN disabled; exact NaN payloads, other rounding modes and exception flags are excluded. Both ARM models share Unicorn implementation, so they are not two independent emulators; the native host cast is the independent result oracle. No expected formatter output is injected.

Both oracle models execute all44 original parser fixtures without external-helper/FP stubs. Unmodified SDK matches38; three contracts differ across two translation states: negative string width, string precision and default float precision. With the string-only candidate,42/44 agree; default `%f` with1.25 still gives stock `1.` vs SDK `1.250000`. Other tested float/special-value cases agree. Default precision difference-1 vs6 explains this observation but is not a complete proof over the entire float domain.

The string branch is inside the shared parser: it cannot replace stock independently without also replacing the unvalidated remainder or retaining executable stock code. Therefore no whole-formatter integration or seven-case run was attempted, and `be4ede3b…` remains current. Next is a stock-default-precision candidate with a wider float corpus and direct ftoa comparison, followed by source-target ABI validation before shared integration.

While holding the formatter, independent startup leaves0x422416/0x4222a0 were reconstructed and tested separately; see `../../inventory-worker/startup-config-leaves/REPORT.md`. No commits, hardware writes or IAR authentication occurred.

## Subsequent default-precision validation

Later stock wrapper/ABI checks and1,104 float fixtures establish the bounded default-precision adaptation; compiled ARM parser1,778 and wrapper288 comparisons pass. Source is now integrated into candidate8ba02bde… pending its seven-case result. This supersedes the prior whole-formatter hold for this bounded candidate; it does not assert exhaustive float equivalence. See `STOCK-FLOAT-CONTRACT.md`.
