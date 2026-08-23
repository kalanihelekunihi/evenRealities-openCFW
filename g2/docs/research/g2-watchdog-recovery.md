# G2 watchdog-driver recovery

Status: clean-room source implementation production-routed on 2026-08-23;
offline behavior, relocation, routing, and package gates green. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path `driver\wdt\watchdog.c` owns two linked bodies
and one literal pool in `[0x0052F2E0,0x0052F38C)`. The 140 body bytes have
SHA-256 `fe30dc1324c0de0255f865ef659ef945608527661b00fc520cb1168e7d9b08a2`;
the 32-byte pool has SHA-256
`26df699091c504939cf2e158811c5464a7a8020f1ba49986afde8d5f87eb667c`.
The full 172-byte object has SHA-256
`4b8cced37db8e7615e81d8c5e27b5d1b5e76edde307c4e6f4834382020acd29c`.

Both names are exact retained diagnostics. `watchdog_init` occupies
`[0x0052F2E0,0x0052F320)` and calls `watchdog_enable` at
`[0x0052F320,0x0052F36C)`. A single exterior call at `0x004C649A` invokes
initialization. The two bodies contain 13 direct calls, predominantly the
local diagnostic expansion.

There are no stored entry pointers, raw entry/interior values, direct
strict-interior targets, or `B.W` entry/interior targets. The next unrelated
body begins at `0x0052F38C`, closing the physical boundary.

## Behavior

Initialization invokes the enable path and emits the retained
`[watchdog]watchdog_init` diagnostic. Enable emits its corresponding retained
diagnostic, calls provider `0x0050938E` with selector zero, reads the returned
byte, and invokes provider `0x00511882` only when that byte equals one. The
first provider is independently observed returning product/configuration
selector pointers elsewhere in stock; the second is kept address-named
because its implementation boundary is not yet closed.

No authenticated historical source or license is available. The independently
authored `components/apollo_main/core_overlay/watchdog.c` therefore implements
the complete decision layer: initialization delegates once to enable; enable
queries selector zero and invokes the retained nPMx provider only for value one.
The two guarded `B.W` redirects replace all 140 stock body bytes with 28 bytes
of strict-relocation source text. The 32-byte diagnostics pool remains retained
compatibility data; the source implementation deliberately omits the stock
conditional logging expansion while preserving the watchdog state transition.

Apple production pins are overlay 165,440 bytes / SHA-256 `922dbcd1…`, Apollo
component 3,688,836 bytes / SHA-256 `1bd34b54…`, and package 4,467,330 bytes /
SHA-256 `04269480…`. The mechanically reconciled reviewed Linux profile is overlay
145,208 bytes / `fac5b48b…`, component 3,668,604 bytes / `378c868e…`, and
package 4,447,098 bytes / `deb4cdb9…`. The Homebrew clang 22.1.8 executable is
not installed on this host, so those Linux pins are derived from the prior
reviewed artifact plus the compiler-identical bounded leaf bytes and still
require reproduction when that reviewed compiler is available.

`tools/analyze_g2_watchdog.py` pins both stock bodies, the retained pool,
names/path, direct-call closure, selector behavior, complete absence of
pointer/interior ingress, source identity, and production registration.
`tests/test_watchdog_candidate.py` exercises all selector outcomes and the init
delegation, and verifies the freestanding Thumb text-symbol surface.

Physical enable/reset timing and reset-cause evidence remain explicitly blocked:
no authorized G2 target, probe, or capture setup is present. No hardware or
flash operation was performed.

The next related compact frontier is retained
`platform\service\eAT\at_buzzer.c`. It has six path-reference sites spanning
`0x005A4FFA..0x005A537C` and directly consumes the newly closed buzzer APIs.
