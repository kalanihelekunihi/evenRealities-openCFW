# Independent review 2149: Type-6 postprocessor at 0x5A0A

**Result: PASS_SCOPED.** Candidate `analysis/touch-sensor-type-six-5a0a-2146/001` remains unaccepted.

Independent Thumb disassembly confirms the 138-byte span [0x5A0A,0x5A94), including initial aggregate-byte bit clear, a reloaded unsigned count doubled into two slots, alternating halfword thresholds and item flag masks, unsigned add/subtract, timer decrement/reload, ordered item-flag clear then zero-timer set, aggregate bit update, 10-byte item stride, and R4-R7/SP restoration.

The isolated 576-case replay compares every timer byte and item byte, aggregate byte, R0/R4/R5/SP against an independent arithmetic model; replay output is byte-identical. Threshold subtraction wraps at 32 bits as the instructions do. Count and parameters remain fixed during each run.

Limit: No child calls occur in this body. The tested memory is synthetic; physical timer/sensor meaning is not established.
Limit: Aliasing and concurrent mutation, including count changes during execution, remain untested.
Limit: No canonical admission or C implementation.
