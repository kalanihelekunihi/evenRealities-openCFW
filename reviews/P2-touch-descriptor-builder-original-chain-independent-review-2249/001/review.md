# Independent review 2249

**Result:** PASS_SCOPED.

The source, `[0x56A4,0x5868)` body, and candidate artifact hashes match the receipt. The isolated replay regenerated all 648 fixtures. Original constructor `0x5548`, field helper `0x51BC`, scaler `0x5528`, and mask helper `0x5188` execute without interception. It asserts each constructor call’s kind/index/destination/context, the full ordered write ledger and 224-byte destination, and R4–R11/SP preservation.

The observed record steps agree with the body: kind 1 advances the working destination by 20 before child mask writes and then by 24, for a 44-byte record step; other kinds advance by 28. Primary, secondary, and group mask construction and mode selection agree with the listing and model, including register-controlled shifts at counts 31, 32, and 255. Pointer reloads used on this path produce the fixture’s asserted writes.

**Limits:** Constructor source fields are zero-initialized and all map entries share one row. List counts are only zero or two, and the replay does not mutate counts/pointers during a pass. This does not verify arbitrary constructor output combinations, changing-list behavior, aliasing, or physical register meaning. No canonical admission is made.
