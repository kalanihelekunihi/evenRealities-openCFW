# Independent review 2589: pre/post callbacks with original pending-work helper

**Result: PASS_SCOPED.** `accepted` remains false.

I verified the candidate's source and artifact hashes and confirmed both body hashes against the mapped source image at base `0x410000`. I reran a copy of its replay with the output directory redirected to a fresh location; all 72 cases passed.

The fixtures cross pre/post entry with pending values 0, 1 and 255, indices 0, 28 and 255, incoming PRIMASK 0/1, and helper base words 0/`0xABCDEF`. Original `0x42CDF8` executes for the 24 post-entry cases with nonzero pending; the child sees PRIMASK set. The checks support the stated ordering: child work precedes pending clear, flag clear, and restoration of the incoming mask. The child field output follows the bounded fixture arithmetic. Parent return is zero even though the child has an incidental R0 result. The replay asserts the relevant writes, arguments, mask at writes, epilogue registers, high-register preservation, and stack.

The child configuration is fixed to gate 1, mode 3, boost 15. Other helper branches, concurrent mutation, physical peripheral behavior, installation ownership, and broader callback reachability remain outside this packet. This review does not admit canonical records.
