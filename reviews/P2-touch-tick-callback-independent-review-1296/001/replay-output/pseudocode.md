# Touch tick callback 35E4

Original 3638 installs odd pointer 35E5 in callback slot zero. Its Thumb body 35E4..35EE is ten instruction bytes, excluding adjacent NOP and literal. Read word at literal address 200008E8, increment modulo 2^32, store it and return through LR. R0 remains unchanged. No frame, helper or interrupt exclusion is used. Five original-instruction fixtures verify exact read/write and overflow behavior. Supplied callback entry proves its local behavior; timer dispatch, tick duration and concurrent access remain unresolved. No canonical admission or C implementation.
