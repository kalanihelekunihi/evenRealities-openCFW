# P2-21033 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47EF74..0x47EFCC (88-byte prefix); instruction/reference output matches candidate. The 40-byte frame stores the helper's full result at SP4, overwriting a saved register slot. Mode dispatch uses LOW8==2; the other route exits to an external continuation with the frame still active. On mode 2, byte SP2 is set, then a fresh word bit-5 test gates a separate read-modify-write/setup sequence. R6 records whether setup ran. Continuation behavior and external helper/global ownership remain unrecovered.
