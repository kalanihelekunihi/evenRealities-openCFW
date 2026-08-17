# SpO2 result callbacks correlation

## Decision

The explicit Ghidra seeds at `0x0004ABEC` and `0x0004ADA0` are independent R1
sensor-stream callbacks, not code owned by the broad noncontiguous function
ranges that happen to contain their addresses.

| Callback | Executable extent | Bytes | SHA-256 | Complete envelope |
| --- | --- | ---: | --- | --- |
| one-shot | `0x0004ABEC..<0x0004ACD2` | 230 | `9013c99396899353c4aac5a7154920955f6de3ac906731b23c6cc4e408c1fea3` | `0x0004ABEC..<0x0004AD40`, 340 bytes, `803aca9ca84c390b65ba559bcc3131fb59c02f75d3d00ad2be84a9bce2ac8578` |
| timing | `0x0004ADA0..<0x0004AE9C` | 252 | `f37ead6711312c1dc90ea1db45c89b0bd16016667a5e9752e66ee73b69485fc8` | `0x0004ADA0..<0x0004AF10`, 368 bytes, `ba960dbad79ba963d6506470bf8fbefe031ab7102818711ab3a92214e766ba30` |

Neither callback has a direct branch caller. The one-shot registration uses
Thumb pointer `0x0004ABED` stored at `0x0004AB2C`; the timing registration uses
`0x0004ADA1` stored at `0x0004B0F8`. Both register topic `"spo2"`.

## Input and adjustment

The fixed six-byte provider record is retained as:

| Offset | Field |
| ---: | --- |
| `0` | raw SpO2 |
| `1` | `r_value` |
| `2` | confidence |
| `3` | signed level |
| `4` | heart rate |
| `5` | mark |

The validity helper accepts raw byte values in inclusive range 70 through 100.
For a valid, health-enabled result, the already transparent GoMore primitive
adjusts around center 96: values below use `(raw-96)*5/10`, values at or above
use `(raw-96)*8/10`, signed division truncates toward zero, 96 is added back,
and the output is clamped to 70...100.

The callback publishes internal event `8` as exactly eight bytes: adjusted
SpO2 at offset zero followed by seven zero bytes. Unlike the heart-rate event,
this record contains no firmware timestamp. `r1_spo2_once_result_plan` and
`r1_spo2_timing_result_plan` return that payload as intent and never dispatch
it.

## Lifecycle

Both callbacks unregister their context from `"spo2"` and clear their stream
handle after valid, invalid, enabled, or suppressed results. The timing variant
also invokes the existing timer-release helper, clears its timer handle, and
sets exactly one completion flag according to the raw validity result. That
valid/invalid flag does not depend on the health-publication gate.

The clean API adds exact six-byte and null-pointer guards. Tests cover all six
fields including negative signed level, both validity edges through the
underlying primitive, transformed values 70→83 and 100→99, byte-exact zero
padding, suppressed and invalid publication, timing flags, cleanup intent, and
invalid arguments.

## Boundary

The two tiny validity/adjustment helpers remain in the separately admitted
transparent GoMore primitives module. Sensor sampling and registration, the
global health gate, event-bus execution, timer release, diagnostic logging,
and live optical control remain external. No biometric value is synthesized
and no private event sender is exposed.

## Verification

```sh
python3 tools/evidence/summarize_r1_spo2_result_callbacks.py
```

The evidence script pins both executable and envelope hashes, both zero
direct-call sets, both registered Thumb pointers, all policy callsites, and
all result/calibration diagnostic strings.
