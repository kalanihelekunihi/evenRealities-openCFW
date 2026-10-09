# UART RX and PCM variant source-ledger reconciliation

The requested UART RX/application-stream and PCM0.7/2.0/2.1 families were
checked against sealed reports, source receipts, and exact stock addresses.
This audit found no uncovered body among the named UART RX entries and no
reason to duplicate their reconstructions.

## UART RX ownership is already closed to the scheduler boundary

| Layer | Existing evidence | Proven software ownership |
|---|---|---|
| HAL RX/FIFO, channel flush `0x55E4EC`, callback `0x5415E6` | `audio-uart-rx-stream-ownership-2026-10-09`: 564 direct + 18 compositions | Channel-1 staging is borrowed until flush. Accepted bytes are copied into the 2,048-byte stream; the callback discards accepted count and the flush clears staging, so rejected suffix is not retained. |
| Stream receive/task copy | `audio-uart-rx-consumer-2026-10-09`: 391 receiver + 216 ring + 4 prefix cases | Receive copies stream-owned bytes into caller storage. Blocking continuation stops at its real task/scheduler boundary. |
| ISR notifier/readiness | `audio-uart-rx-notifier-2026-10-09`: 1,440 direct + 36 compositions | Accepted data can move a waiting task to ready or pending-ready ownership and set the software yield flag. No PendSV delivery is claimed. |
| Codec UART3 direct IRQ | `audio-codec-uart-irq-delivery-2026-10-09`: 112 cases | FIFO bytes accumulate in staging, callback copies them to the newest-63-byte ring, and accumulated count resets after delivery. |
| Codec ring drain | `audio-codec-uart-rx-drain-2026-10-09`: 320 cases | Caller receives a copy of retained ring bytes; no device-response timing is inferred. |

The earlier successor row naming `0x58E618`, `0x5415E6`, and `0x55E4EC` as
pending was stale. The remaining RX boundary is a complete live task handover
and physical UART/IRQ timing. Existing notification block/wake/resume batches
prove the analogous RTOS software transitions under controlled ordering, but
combining them does not create an observed exception or device schedule.

## PCM variant coverage

PCM0.7/2.0 is source-backed for GPU on/off, temperature classification and
publication, sleep preparation, hardware temperature application, postpone and
pending drain, TON initialization/update, LP automatic switching, before/after
callbacks, variant initialization, and original-trim capture. The principal
receipts are:

- `audio-early-pcm-gpu-closure-2026-10-08`: 5,622 comparisons.
- `audio-early-pcm-pending-closure-2026-10-08`: 6,888 comparisons including
  earlier regressions.
- `audio-trim-initialization-closure-2026-10-08`: 1,310 comparisons.
- `audio-early-pcm-dispatch-closure-2026-10-09`: 442 direct/composed plus 748
  initializer/composition cases; 608 are reused initializer regressions.

PCM2.1 outer control, preparation/state-change/planner/apply, TON/completion,
lifecycle, and default reset are covered by the control, children, completion,
and reset batches. The final reset ELF reports 7,720 comparisons including
family regressions. PCM2.2's complete 27-entry transition table is separately
covered by 12,019 comparisons.

The true tempco-suspend wrapper is `0x4803DC`, registry slot 10. Across 168
sealed registration fixtures, stock installs no slot-10 child. Public SDK code
under `NO_TEMPSENSE_IN_DEEPSLEEP` therefore cannot be promoted to an active
stock body. Runtime mutation could change the table, but no such writer or
trace is established. Two early reset-looking callbacks at `0x5A0018` and
`0x5A0A6C` are instruction-proven zero-return no-ops; they must not be expanded
into invented reset sequences.

## Genuine residuals

The complete enclosing common low-power initializer is also already recovered
by `audio-clock-reset-active-2026-10-08` (1,392 comparisons including clock
recovery). The remaining useful static work is actual CPU power-mode
wrapper/caller attribution and UART3 TX interrupt drain if app-facing codec
transport needs further closure. Authentic calibration/trim selection, active
runtime callback-table contents, PendSV/NVIC delivery, peripheral timing, and
physical power settling require runtime/device evidence.

No new comparison count is claimed by this reconciliation. Re-running sealed
fixtures or recopying public source would increase activity without increasing
function coverage. Whole-image source inference remains incomplete, while the
named UART RX and registered PCM variant bodies are exhausted within their
documented static contracts.
