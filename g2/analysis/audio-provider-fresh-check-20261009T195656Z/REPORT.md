# Fresh provider scan: execution blocker

The unchanged notification verifier exited 132 (SIGILL) before producing comparison results. Python 3.13.15 and importing Unicorn succeed on this arm64 host; no fresh instruction-execution pass is claimed. Exact native crash cause is not established. Resolve the Unicorn execution/runtime failure or supply a working equivalent offline execution environment before further dynamic validation. No tool reinstall or environment change was attempted.

Existing sealed provider recheck reports 704 notification comparisons and 245 codec/HAL compositions, zero differences. Those historical results are unchanged. Blocking wait 0x455B84 reaches insertion 0x455FA8 and stops before yield 0x4420BC. Current/overflow delayed-list selection and indefinite suspended-list insertion are covered; actual exception delivery/resumed scheduling are not.

The previous supported invalid-handle path clears channel active before HAL returns status 2; close returns -1 with codec-open retained. Subsequent host initialization skips enable and ignores baud failure. Explicit RX callback followed by close/reopen/read retains bytes 10 20 30. These establish software behavior under fixtures, not physical power or IRQ behavior. Actual HAL power/configuration bodies execute in those historical comparisons; GPIO/domain/clock boundaries remain supplied providers. Unused configure_result fixture fields do not add failure coverage.

Source-ledger review: latest final static successor and bounded final pass identify no further nonduplicate source closure in the selected audio/UART/power scope from currently bound inputs. Authentic vector/NVIC/PendSV/task traces, callback/calibration/INFO1 runtime state, GPIO frontend bindings, physical observations, or unavailable ROM/private providers are required. This is a local scope boundary; whole-firmware P2 is not exhausted.

Preservation was checked with all legacy seal writes intercepted. See preservation.json for exact seal/input/checkpoint outcomes and attempt.json for observed index hashes. No Git mutations, production edits, canonical-ledger updates or device writes occurred.

Evidence: ../audio-provider-recheck-2026-10-09/REPORT.md; ../audio-codec-lifecycle-hal-composition-2026-10-09/REPORT.md; ../audio-notification-block-insertion-2026-10-09/REPORT.md; ../source-ledger-final-static-successor-2026-10-09/INDEX.md; ../source-ledger-bounded-pass-final-2026-10-09/REPORT.md.
