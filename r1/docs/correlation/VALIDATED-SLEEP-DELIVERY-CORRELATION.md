# Validated sleep delivery and storage correlation

Status: three R1 product functions / 850 executable bytes byte-pinned; bounded admission,
fallback, append, and post-storage policy implemented.

## Closed call chain

| Entry | Bytes | SHA-256 | Role |
| --- | ---: | --- | --- |
| `0x0005B890..<0x0005B9AC` | 284 | `817a0854d1adce8db5bdbde8eb88bc34f235a5ebde7308ff576bb279623eaa53` | two-attempt journal append and rollover |
| `0x0008DC94..<0x0008DD18` | 132 | `5c5baba208acd202ffc19aad32ad644b708259ff6989b976af31c93b8bad429b` | storage result and automatic-sync orchestration |
| `0x0008DD90..<0x0008DF42` | 434 | `5f375de1093b593b9df32fa774b51ffa063e7086884562e01633838373530e6c` | one-hour admission, private storage event, and direct fallback |

`../../tools/evidence/summarize_r1_validated_sleep_delivery.py`
authenticates the application, all three bodies, their complete direct caller sets, related
storage and automatic-sync branches, state literals, and diagnostic strings. The 434-byte ingress
has the sole caller `0x00042960`; storage-task thunk `0x00042BC6` and the ingress fallback at
`0x0008DF3C` converge on the same consumer.

## Functional contract

- The event-`0x000D` ingress computes `endTimestamp - startTimestamp` as wrapping UInt32 and
  admits the session when the result is at least 3,600 seconds. Exactly 3,600 passes.
- A passing record is posted as private storage event `0x2000` with the wrapping UInt16 length
  `32 + compactStageCount`.
- A failed event post invokes the same storage consumer directly, so queue failure does not drop
  the record.
- The storage consumer ignores null input, appends nonnull data, and requests automatic sync with
  argument `6` only after a successful append.
- The appender accepts at most 3,888 bytes, makes at most two complete
  find-writable/rollover/write attempts, and returns success on the first successful write.

The stock unsigned subtraction also admits a backwards timestamp after wrap. The clean-room
planner reports that condition with `timestamp_wrapped`; downstream typed sleep validation still
rejects an end timestamp below the start timestamp. This preserves the recovered route decision
for analysis without treating corrupt time as valid persistent data.

## Ownership and safety boundary

These functions contain R1-specific sleep lifecycle and persistence policy, not Nordic, GoMore,
Goodix, or FlashDB provider implementation. OpenR1 implements the ingress and post-storage
decisions as pure planners in
`../src/r1_health.c`, while the bounded two-sector
journal in `../src/r1_sleep_db.c` supplies the already
tested two-attempt append behavior over the caller-provided flash interface.

The recovered logging/event frameworks and live task dispatch remain external. The stock path's
destructive reset after two failed writes is not preserved; OpenR1 returns `R1_ERROR_STATE`,
allowing deployer-owned recovery policy to decide what happens next. Tests pin the 3,599/3,600
boundary, wrap report, event ID and length, queue-failure fallback flag, null/failed/successful
storage outcomes, automatic-sync argument `6`, maximum append size, two attempts, rollover, and
failure without destructive reset.

Reproduce the evidence check with:

```sh
python3 tools/evidence/summarize_r1_validated_sleep_delivery.py
```
