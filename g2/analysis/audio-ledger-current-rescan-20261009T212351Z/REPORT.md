# Audio source-ledger current rescan

The requested notification insertion and codec/HAL composition are already closed at their supported offline boundary. This scan verifies the existing evidence rather than repeating fixtures without new source or runtime input.

- 3,684 sealed entries match; all 110 authenticated inputs and four checkpoints match. The observed index SHA-256 remained `4a26921e98972835ec957e85fcb4fa0c78ffc7ef95b73cb107c837293b574f48` throughout this scan. This is an observed current index, not a claim that unrelated work never changed the historical index.
- Both existing native ELFs and every source in their reproduction receipts still match. Historical results remain 704 notification and 245 codec/HAL comparisons, zero differences; these counts are not newly executed tests.

## Confirmed software behavior

Notification wait at `0x455B84` reaches insertion at `0x455FA8`: remove current ready item, sort finite deadlines into current/overflow delayed lists, or use the suspended list for permitted indefinite waits. Selected writes occur under BASEPRI `0x30`. Positive waits stop before yield `0x4420BC`, so this does not establish scheduler delivery or a blocking round trip.

Codec initialization resets the 64-byte ring only on first initialization. Close/reopen preserves previously buffered `10 20 30`, drained by the subsequent reader in the explicit callback fixture. No claim is made about bytes arriving on closed physical hardware.

Supported invalid-handle close clears descriptor active before HAL rejects the handle (status 2). Codec close returns -1 without clearing open. Subsequent host initialize skips enable, ignores baud failure, and returns success with initialized/open set and active clear. This is a software state mismatch, not a physical power failure.

Power/configuration comparison executes stock HAL bodies and reconstructed HAL source. Domain/clock/GPIO providers remain supplied fixture boundaries. Status 7 from domain/clock providers is ignored in the tested power paths; it cannot prove hardware enable/disable failure. The historical `configure_result` fixture field is unused and supplies no configuration-failure coverage.

## Exhaustion and exact next input

No additional nonduplicate closure is established for this selected audio/UART/power source ledger. Continue only with image-bound vector/NVIC/PendSV/task-selection traces, authentic callback/calibration/INFO1 state, GPIO frontend bindings, physical UART/clock/power observations, or authenticated missing ROM/private source. Broader whole-image P2 remains unfinished and is separate work. No firmware patch, production edit, canonical ledger update, Git mutation, or device write occurred.

Existing evidence: [provider recheck](../audio-provider-recheck-2026-10-09/REPORT.md), [notification tests](../audio-notification-block-insertion-2026-10-09/REPORT.md), [codec/HAL tests](../audio-codec-lifecycle-hal-composition-2026-10-09/REPORT.md), and [remaining ledger](../source-ledger-final-static-successor-2026-10-09/INDEX.md). Machine-readable preservation and receipt checks: [scan.json](scan.json).
