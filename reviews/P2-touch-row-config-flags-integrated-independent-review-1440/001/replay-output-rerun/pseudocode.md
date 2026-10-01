# Validator with complete local flag helper chain

Original 6384 now executes original 6294 in addition to all recovered range, threshold and shift helpers. Only A6C0 and A7CC remain controlled with unsigned quotient/remainder responses. Initialized percentage, decision-mode and context fields are zero: the 6294 path calls A6C0(0,100) then A7CC(0,1) and returns flag 4. The parent stores that byte while retaining its original flags for later decisions.

The 216 fixtures check exact division calls, row writes, final status and restored frame. Wider helper inputs are separately exercised in 1437/002 and the earlier helper packets. Division bodies, mixed flags, pointer validity and physical meaning remain unresolved. No canonical admission or C implementation.
