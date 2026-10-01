# Mixed-row state checks for 6384

This extends the complete local-flow packet 1413 with 729 original-instruction fixtures. Each of three records independently selects mode 0, 1 or 10 and width 0, 8 or 4097. Flags and signed bytes are zero, so no helper boundaries are reached. The independent model checks that modes 1 and 10 set minimum to 8, other modes set status 1 while retaining the earlier minimum, and out-of-range widths immediately replace status with 2048. Exact return, stack restoration, empty helper trace and absence of row writes are checked.

Helper effects and mixed flags remain covered only by the controlled uniform-row fixtures in 1413. Physical behavior and pointer validity remain unresolved. No canonical admission or C implementation.
