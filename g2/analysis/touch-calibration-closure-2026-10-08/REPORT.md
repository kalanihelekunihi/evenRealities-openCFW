# Touch baseline calibration and hold parameter consumers

New [offline C](../../components/touch/calibration_offline/README.md) reconstructs the saved-baseline getter/save, proximity classifier, report/calibration path, gesture initialization and two sensor-status queries. It composes preserved native EEPROM source. **Original gesture machine `0x4070` and speed helper `0x3efc` remain borrowed executable dependencies**, not fully source-defined closure. No production payload, index, shared state, device or commit changed.

## Baseline updates and report ordering

Record baseline `u16+4` is the saved reference used by classifier `0x441c` and report builder `0x3b24`. Getter `0x3a1c` returns zero unless magic equals `0x45564e55`; it checks neither readiness nor a fresh storage read. Command 6 reads the RAM baseline directly.

Widget 2's sensor record has `u16` fields at offsets 0, 2 and 4, and a status byte at 6. The application uses these as raw sample, baseline sample and difference. Addresses and widths are instruction-proven; electrical units and how scanning updates them remain unverified.

Command 5 sets flag `0x200009cf` and acknowledges before calibration. Report processing first obtains widget 1 activity/position, computes proximity change and executes the gesture machine. **No proximity transition and no gesture event means an early return:** the calibration flag remains pending.

Once a report runs, it snapshots the saved baseline and computes the absolute unsigned difference between the current sensor baseline and record baseline. Difference **49 is skipped; 50 updates**. It writes the new baseline to RAM before persistence, then clears the flag after an attempted or skipped save. There is no new calibration-completion acknowledgement. Lower flash errors can be discarded; failed programming does not roll back RAM.

The 16-byte report contains event bytes 0–3, then little-endian sensor baseline at +4, raw at +6, difference at +8 and **old saved baseline at +10**. The getter runs before calibration, so this report carries the old value even when the update succeeds. The last four report bytes retain their prior contents. Processing copies 16 bytes to I2C TX, arms a 16-byte read buffer, writes GPIO offset +0x44 = 1 and sets report flag `0x200009cc = 1`, countdown `0x200009c8 = 640`. This proves call/memory behavior, not delivery or countdown duration.

## Proximity boundaries and corrected query label

Classifier initially chooses code 2 for nonzero widget-2 sensor status, code 1 otherwise. With a valid nonzero saved baseline B:

- Sensor baseline > B + 500 overrides to code 2.
- Sensor baseline < B and raw <= B + 49 overrides to code 1.
- Other combinations retain the status-derived code.

It compares the desired code with byte `0x200009d8`: unchanged returns 0; a change stores the code and returns 1 or 2. Baseline zero bypasses numerical overrides. This is not a symmetric threshold test or established physical on/off meaning. Samples/reference are `u16`; additions promote to 32 bits without wrapping at 65535.

Historical symbol `0x7d36` called the query a raw-count read. Actual instructions return **byte +6 status**, only for widget type 6 and a valid sensor index. `0x7d04` reads active bit 0 from widget runtime +35 except type 7. `0x7d6c` returns widget context +36, which contains a pointer to position data for types 2–5. Report position uses the low eight bits of the resulting `u16`. Native report fixtures require valid types/pointers; malformed/null position behavior is not generalized.

## Parameter is a hold threshold

Record parameter `u16+6` initializes the 80-byte gesture state at `0x20000940`; zero becomes 1000. Bootstrap normalizes a saved zero in RAM, and gesture initializer `0x404c` independently normalizes zero input. Command 7 accepts all nonzero `u16` values, updates RAM record and active parameter, and defers restart/persistence. Restart clears all 80 state bytes before installing the threshold. Baseline and hold parameter are separate fields.

Stock gesture code computes unsigned counter elapsed time from the current counter minus press start. With position displacement <= 24 it tests elapsed >= the first state `u16`. Original stationary-hold traces produce **`10 00 00` precisely at the threshold**, not one count before it, including parameters 1 and 65535. These traces use original gesture code and do not establish independent gesture reconstruction or all swipe/multitap branches.

Counter `0x200008e8` is incremented modulo 32 bits by callback `0x35e4`. Startup `0x3638` sets its initial value from R0 (main passes 0), calls SysTick initialization with source 0 and reload 40, and installs callback `0x35e5` in slot 0. Original instructions execute against synthetic MMIO: CTRL = 3, LOAD = 40, callback table `0x20000f40`. Pinned PDL `cy_systick.h` defines source 0 as `clk_lf`. Thus parameter 1000 means **1000 delivered callback increments**. LF clock frequency, latency, coalescing and sleep behavior are not measured; no milliseconds conversion is asserted. Software-delay argument 10 is separate.

## Validation and limits

ELF SHA `e9a4521cbeaac084884bd16c1144dd468f0db58eab344a846f33e63423c4a4a0`.

| Evidence | Result | Boundary |
| --- | --- | --- |
| Composed report/calibration original/native | 336 PASS | Original gesture executes in both; native storage/provider/CRC; synthetic SROM |
| Gesture initialization original/native | 16 PASS | Parameters 0/1/1000/65535 and all valid/null argument combinations |
| Stationary hold original-only | 12 traces PASS | Threshold−1/threshold/threshold+1; no native gesture-equivalence claim |
| Counter setup/increment original-only | Setup + 3 increments PASS | Synthetic SysTick memory, not actual interrupts/clocks |
| Negative controls | 3 rejected | Calibration at 49, new baseline in the same report, proximity at 500 |

Coverage is 292/316 report instruction bytes and 90/90 classifier bytes. Unvisited report paths include the original gesture-null fallback and write-error logging. Discarded driver errors do not force an upper write failure in this blank-history fixture; the prior bootstrap selective-history failure is separate evidence.

The 336 cases cross saved baseline 0/1000/65000; delta −50/−49/0/49/50/500/501; sensor status 0/1; prior code 1/2; pending flag 0/1; and success/program-error models. Samples are explicitly clipped to 0–65535. Compared record, gesture state, report, TX, flags, proximity, I2C context, storage, EEPROM context, ordered SROM requests, GPIO, SP and PRIMASK. Report logging is compiled out and its invocation intentions are not compared.

The next concrete source closure is the 874-byte gesture machine and 324-byte speed helper, using these parameter/layout fixtures. CapSense sample production and LF-clock setup remain actionable SDK/static leads, not exhausted dependencies. Analog behavior, physical cadence, IRQ races and durability need further closure or actual captures. Exact producing SDK revision remains ambiguous; this batch claims no new exact compiled-byte total.

Fresh preservation checks match 110 locked inputs, 310 prior sealed files and four accepted checkpoints. No whole-OTA completeness, deployability or byte-equality claim.
