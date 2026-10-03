# Independent review 2459

**Result:** PASS_SCOPED.

Candidate: `g2/build/pseudocode-first/20260930T190500Z/analysis/touch-mode-two-original-loader-transition-2458/001`. Receipt SHA-256 `357b86c8951a13137e64b5830d5d30d73233c46b14058802833ebbebd480aa8e`; all declared artifact hashes match. Both body ranges match the pinned source image hash `371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87`.

I replayed the harness into an isolated output directory; all 160 cases pass. The matrix crosses five prior modes (0/1/5/6/7), all eight selector values, two configuration/factory patterns, and zero/all-set descriptor flags. Original 6AC0 and 8FD0 run; the three port helpers are the only controlled firmware calls. Assertions cover their arguments, loader arguments, preparation clears, the complete ordered write ledger, old/new mode and status, and R4–R11/SP.

The loader copies its configuration regions before selector dispatch. Selectors 0/3/6 take the modeled factory-byte success branch; other selectors return an error after the earlier configuration copies. The enclosing dispatcher reports 64 and preserves the old mode on those failures, even though earlier peripheral writes occurred. On the tested success path it performs the expected peripheral writes/readbacks and stores mode 2. These conclusions match the replay's ordered-write and final-state assertions.

**Limits:** Factory bytes and peripheral reads are modeled inputs, so physical MMIO behavior is not demonstrated. The controlled port helpers return `0xFFFFFFFF`; their real effects are not established. Aliasing and integration with the full measurement chain remain open, as do prior literal/table ownership limits. Bounded private evidence only; accepted:false, no canonical admission.
