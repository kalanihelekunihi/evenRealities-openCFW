# PMIC-charged notification correlation

## Decision

Ghidra records `0x00096CC8` as one 374-byte function with two noncontiguous
executable ranges: `0x00047F10..<0x00047F9A` (138 bytes) and
`0x00096CC8..<0x00096DB4` (236 bytes). Concatenating those ranges in address
order gives SHA-256
`a00d2417c36d598e48d0372052fabccf0444ea0ced5a0252ba33983ad912a34f`.
The two direct callers are `0x00046218` and `0x000463D4`; the main range enters
the scattered completion block through the `B.W` at `0x00096D66`.

The routine is R1 product orchestration rather than Nordic, CMSIS, ST, or
another vendor implementation. It is admitted as `r1_product_specific` /
`clean_room_behavior_only`. The clean implementation is the pure
`r1_pmic_plan_charged_notification` policy in
`../src/r1_battery.c`.

## Recovered retry policy

The single UInt8 state byte has a special `0xA5` marker. The marker is cleared
before testing charge state; an immediate not-charging result cancels callback
`0x00096A61` and sets thread flag `0x10`. Other marker outcomes continue with a
zero retry count.

Normal retry eligibility is exact and conjunctive:

- current-sense voltage is strictly below 50 mV;
- battery voltage is strictly below 4,200 mV; and
- the old retry byte is at most 12.

The byte is post-incremented with UInt8 wrap before the last test. An eligible
charging/other state requests the recovered GPIO recovery pulse for 200 ms and
schedules callback `0x00096A61` after 409 ms. A full state clears the counter
and enters completion. A not-charging state enters completion while retaining
the incremented counter. A failed voltage gate or an old count above 12 clears
the counter before completion.

## Recovered completion policy

Completion first requests an ST25DVxxKC dynamic interrupt-status read. If that
read succeeds and the status is zero, a fresh not-charging observation takes
the short path: cancel retry work and invoke the existing charge-event policy
with event byte zero. If the status is nonzero and bit `0x08` is set, the plan
requests closure of touch-service source 1.

All remaining paths cancel retry work and request an ST25DVxxKC dynamic mailbox
control read. A zero first status requests `SetMBEN_Dyn` followed by a second
read; the event byte passed to the existing charge-event policy is the second
status. A nonzero first status is used directly. The normal completion tail
then schedules callback `0x00042D29` after 5,120 ms and requests the abstract
device callback `0x00042D2F`.

The clean observation structure retains the three charge-state samples as
separate fields because the recovered routine calls the classifier at three
different decision points. An executor may collect those observations lazily;
fields for paths not taken are ignored.

## Provider boundary

This closure does not recreate:

- Nordic GPIO configuration or the 200 ms CMSIS delay used by the recovery
  pulse;
- ST25DVxxKC `ReadITSTStatus_Dyn`, `ReadMBCtrl_Dyn`, or `SetMBEN_Dyn`, which
  remain supplied by the pinned official ST component;
- Nordic SAADC sampling, CMSIS thread flags, or timer primitives;
- the separately recovered delayed-event loop;
- touch-service internals, generic device-registry operations, or logging; or
- the existing R1 charge-event planner at `0x00096AD0`.

The result contains only R1-owned thresholds, sequencing, state transitions,
and provider action requests. It performs no live GPIO, mailbox, timer, thread,
touch, or device-registry operation.

## Verification

Host tests cover the strict 50/4,200 mV boundaries, old retry counts 12 and 13,
the `0xA5` marker short path, charging/full/not-charging outcomes, the retained
not-charging increment, interrupt bit `0x08`, both mailbox status branches, and
invalid pointer immutability. The evidence summarizer pins both scattered code
ranges, their combined digest, both callers, the scatter transfer, and all four
callback literals.

The planner is retained at nonzero address `0x000372E4` in the verified
unsigned Nordic SDK image. That image contains 94,804 bytes of text, 236 bytes
of data, and 132,544 bytes of BSS; its standalone BIN is 95,040 bytes. The HEX
and BIN SHA-256 values are
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.

Reproduce the closure with:

```sh
python3 tools/evidence/summarize_r1_pmic_charged_notification.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
