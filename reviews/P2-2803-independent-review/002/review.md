# Independent review 2803 — handler 0 normal chain, corrected candidate

**Result: PASS_SCOPED.** This append-only review binds to candidate 2802/002, which corrects the body range/hash identified in review 2803/001. The receipt body hash now matches the locked image interval `0x427E84..0x42805A` (470 bytes, 160 decoded instructions), all candidate artifact hashes match, and the isolated replay passes all 64 fixtures.

The fixture scope remains control bit 0 clear and indices 0/1 with the documented endpoint, target-pattern, cache, protection, and mask combinations. The replay asserts ordered publication/control/cache writes, original secondary helper and delay paths, 2,210 ITCM iterations, packed return, and frame/register/mask preservation. Equal-index and wait/service paths, broader states, physical hardware, concurrency, and incoming ownership are not established. `accepted` remains false.
