# Independent review 1795: scoped pass

Both instruction spans match: 4860..486C (12 bytes/5 instructions) and AA2C..AA3E (18/9); alignment at AA3E and following self-loop at AA40 are excluded. All 40 isolated fixtures reproduce exact source-byte reads, destination-byte writes, memory result, returns, SP and stop PC. AA2C copies forward one byte at a time and returns the original destination; 4860 forwards original R1/R2 with R3 as destination, ignores provider R0 and returns zero. The +3 overlap fixtures confirm forward-propagation behavior.

This establishes only bounded behavior over synthetic RAM. No physical storage or canonical coverage claim follows.
