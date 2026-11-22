# Gesture speed helper — source-linked C

`touch_gesture_speed` reconstructs helper `0x3efc` using an 80-byte state.
Three 8-byte entries start at +48: position byte +0, timestamp u32 +4.
Ring index +72 is 0–2, sample count +73 saturates at 3, filtered speed +74
is a byte and direction +75 is signed −1/0/+1. Valid state and stable samples
are preconditions; timestamps use delivered firmware counter increments.

This standalone module has no retained executable firmware dependency. The
touch source-linked report path now reaches it through the C gesture machine.
Its original-instruction comparisons are offline; electrical speed, physical
time and interrupt scheduling remain unverified. The earlier composed test
retained the original gesture machine while replacing only its speed helper
in guest memory. See the associated analysis report for formulas and limits.
