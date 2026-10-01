# Independent review 2157: Original copy in type-2/3 postprocessing

**Result: PASS_SCOPED.** Candidate `analysis/touch-sensor-type-two-three-original-copy-2154/001` remains unaccepted.

The isolated 864-case composition replay matches the candidate byte for byte. Original 5A94 and AA2C execute; the 48CC/4A2A constructors are controlled to write two known eight-byte entries. The caller passes the observed scratch/destination arguments and the original copy helper writes both payloads in order.

Assertions cover the resulting 16 bytes, threshold/countdown/item/aggregate behavior, constructor order, copy arguments, and R8/SP. When no constructor runs the output/count remain zero in the tested cases. This is a controlled-child composition, not a recovery of constructor behavior.

Limit: Constructors 48CC/4A2A remain controlled; arbitrary constructor output/count, aliasing, concurrency and physical sensor meaning remain unresolved.
Limit: No canonical admission or C implementation.
