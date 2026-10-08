# Independent review — P2-21461

Status: partial; accepted: false.

Fresh replay passed for the 130-byte span. Regenerated instruction and reference files match the candidate exactly, including byte tiling and PC-relative targets.

The first frameless predicate loads owner+68, returns zero for null owner/head or a head status other than one, and otherwise returns the head pointer. The zero halfword at 0x484A0E is retained as an inter-function alignment slot; it is not included in either neighboring routine's executed control flow. The helper wrappers use the observed 16-byte frame, ordered calls, and live arguments. Their POP {R0,R4,R5,PC} restores entry R3 into R0, so the helper return values are not the wrapper return.

Helper contracts and caller ABI are not established. Review remains partial/unaccepted.
