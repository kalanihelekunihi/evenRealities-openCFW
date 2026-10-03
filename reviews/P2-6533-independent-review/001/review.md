# Independent review 6533

Disposition: **PASS_SCOPED**; `accepted:false`.

Both packet source ranges and all packet files match their pinned hashes. GNU Thumb decoding confirms the first wrapper computes `arg0 + arg1 - 1` with 32-bit wrap and discards the result. It initializes the global cache only when the fresh word at the literal address 0x200270C8 is zero, calls 41D792(1, SP), ignores status, and stores the word at SP+0x2C. It then returns 0 when arg0 < 0x4000; otherwise it freshly compares arg1 against the cached global and returns 1 exactly when arg1 is unsigned-less-than that value.

The next two wrappers call that guard with (arg1,arg2) and (arg0,arg2), respectively. A false guard returns 0xFFFFFFFF; a true guard calls 41568C or 430B10 with the original three arguments, ignores the child return, and returns zero. The final wrapper checks the guard on (arg0,4); on success it executes two NOPs and returns zero without another memory operation in this body. In 430B10, the third argument is transformed as wrapped `(arg2+3)>>2`; the wrapper saves PRIMASK, calls 42E4F4 with literal 0x12344321, arg1, arg0, and that rounded count, ignores the child result, restores the saved mask, and POP returns the incoming R3 slot in R0.

This is limited to these ranges and does not assign external child semantics or hardware purpose. No canonical files or gates changed.
