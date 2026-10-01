# Independent review 2143: Sensor type dispatcher at 0x5BA2

**Result: PASS_SCOPED.** Candidate `analysis/touch-sensor-type-dispatch-5ba2-2140/001` remains unaccepted.

Independent Thumb disassembly confirms [0x5BA2,0x5BC0) is 30 bytes: save R4/LR, load unsigned byte [R0+123], dispatch values 2/3 to 0x5A94 and value 6 to 0x5A0A, then restore R4 and return. Other values bypass calls.

The isolated 512-case replay covers all 256 type bytes and both controlled child R0 results. Child entry hooks assert R0 is the incoming row and R1 is context; their controlled return value propagates unchanged. Non-dispatch values return the row pointer. R4 and SP assertions hold, and isolated JSON is byte-identical to the candidate.

Limit: Both selected children remain controlled; their behavior is not established.
Limit: Context/row fixtures do not prove physical sensor meaning, aliases, concurrency, or caller completeness.
Limit: No canonical admission or C implementation.
