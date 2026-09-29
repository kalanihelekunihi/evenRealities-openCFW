# Reference pseudocode for binary-only vendor libraries

These C files re-express vendor libraries that have no public source: GoMore
health algorithms, Goodix HR/SpO2/HRV algorithms and heap, GXT310, QMA6100,
YHM2710, and several unidentified device, sensor-stream, calendar and RTC
frameworks. Each is tied to its stock addresses in the correlation records
under [`../docs/`](../docs).

They were written for the retired clean-room implementation. They are
**not** byte-matched and are not part of any build. Use them as reviewed
pseudocode that seeds the byte-matching phase, not as source that
satisfies it. `model_data/` holds constants extracted from the official
application by `../tools/generate_r1_model_data.py`.
