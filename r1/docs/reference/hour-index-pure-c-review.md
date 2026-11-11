# R1 local-hour query in ordinary C

The local-hour entry at `0x5aca6` now uses a private, zeroed eight-byte canonical calendar object in C. It obtains the signed cached RTC/calendar offset, calls the UTC converter with the timestamp bit pattern, ignores its status as stock, and returns the unsigned hour byte. The separate nonstock preparation helper and assembly frame bridge are removed.

A raw direct-branch scan identifies seven callers in hourly averaging, five sensor-cache paths and daily replay. Their visible post-call flow consumes the scalar R0 result. The C interface does not promise caller-scratch R2/R3 contents or native private-frame addresses. The scan does not establish indirect-call coverage.

Validation passes 2,655 stock/C hour and average comparisons, including partial calendar writes, converter status zero, timestamp/offset boundaries and all four rounding modes. All 30 native hour instruction bytes execute. Another 1,560 comparisons execute the real C offset getter, UTC adapter and Gregorian converter with the source-owned cached RTC/calendar and hourly/stress state. An independent wrapped-hour oracle checks results. Cache bytes and full FPSCR results match. Five compiled defects are rejected.

The averaging function's source text, executable section bytes and normalized relocations remain identical. Its `VCVT` assembly remains because the current implementation explicitly preserves saturation and exception behavior, including count wrap. This stage does not replace that architectural primitive with an undefined out-of-range C cast.

The tested object matches the normal build. The other 852 prior nongenerated objects remain identical. No persistent state is added; the manifest, source-plan selections and imports remain unchanged: 863 compiled units, 63 application imports and 22 bootloader imports.

[The receipt](hour-index-pure-c-review.json) records hashes and proof boundaries. Calendar/offset/logging providers are modeled in the direct fixture; only logging is modeled in the real-converter fixture. Physical clock hardware, concurrency, final source linking and boot remain unverified.
