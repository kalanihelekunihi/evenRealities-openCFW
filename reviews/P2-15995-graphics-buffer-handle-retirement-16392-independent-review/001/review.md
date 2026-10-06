# Independent review 15995

Partial, accepted:false. Fresh decode replay passed for 44 bytes. Null handle path calls diagnostic and returns FFFFFFFF. Nonnull path: negative handle word +28 skips child; otherwise child 514026 runs. Negative child result skips rewriting +28; nonnegative result writes FFFFFFFF. Both nonnull paths return zero.

Child/global/hardware effects remain unqualified; no admission or gate change.
