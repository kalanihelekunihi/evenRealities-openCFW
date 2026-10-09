# Notification and codec provider recheck

Fresh offline execution reproduced **704 notification comparisons and 245 codec/HAL compositions, with zero differences**. Existing verifier scripts were executed unchanged; their writes were intercepted and captured here, preserving old results and seals. Both native ELF hashes match their sealed receipts. No rebuild, Git mutation, production edit, canonical ledger update or device write occurred.

Notification insertion at `0x455FA8`, reached through wait `0x455B84`, removes the current ready item, selects current/overflow delayed lists using unsigned deadline wrap, and handles indefinite waits with the suspended list. Selected state writes execute under BASEPRI `0x30`. Positive blocking cases stop before yield `0x4420BC`; this does not establish PendSV delivery, task selection or resumed return.

Codec lifecycle executes stock HAL power/configuration bodies on the original side and recovered compiled HAL bodies on the comparison side. The sequential initialize/RX-callback/close/reopen/read fixture retains and drains `10 20 30`: close/reopen does not reset the ring. Callback invocation is explicit, not hardware IRQ delivery.

The supported invalid-handle path reproduces failed-close mismatch: channel active is cleared before HAL validation; HAL status 2 propagates to codec close -1, leaving codec-open set. Subsequent host initialize skips enable, ignores baud failure and returns success with initialized/open set and active clear. This proves software control flow under the fixture, not physical peripheral state.

Injected peripheral enable/disable and clock provider status 7 is ignored by recovered HAL power control in the tested paths. It therefore cannot demonstrate physical power failure. GPIO and domain/clock providers remain fixture boundaries; the UART configuration body is executed, not replaced by a synthetic configure return. Historical `configure_result` fixture fields are unused by this composed verifier and provide no extra configuration-failure coverage.

## Evidence and stopping boundary

Captured full comparisons are in the two successor results JSON files. Original source/address bindings, build hashes and provider hook definitions remain in the sealed predecessor directories:
- `../audio-notification-block-insertion-2026-10-09/`
- `../audio-codec-lifecycle-hal-composition-2026-10-09/`
- `../source-ledger-final-static-successor-2026-10-09/INDEX.md`

The selected audio/UART/power ledger has no further nonduplicate source-ledger closure established from currently bound inputs. Continuing requires vector/NVIC/PendSV/task-selection traces; authentic callback/calibration/INFO1 runtime state; GPIO frontend/source bindings; physical UART/clock/power observations; or authenticated unavailable ROM/private providers. Broader whole-image P2 remains open. Repeating fixtures does not close these boundaries.

Preservation verifies prior seals, all 110 inputs and four checkpoints. The observed Git index is recorded and stable during this check; it differs from the historical scan baseline, so this receipt does not assert that other ongoing work made no earlier index changes.
