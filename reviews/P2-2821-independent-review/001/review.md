# Independent review 2821 — slot 44 service chain

**Result: PASS_SCOPED.** Source and ITCM image hashes, all eight body hashes, and all declared candidate artifact hashes match. The isolated 384-fixture replay passes. It runs the original slot-44 dispatcher, service, conditional flag restores, runtime stop, operation-4 dispatcher, and inactive query/disable path without firmware interception.

The fixture confirms the dispatch result is the incoming saved R7 value, not the service return, and checks the ordered writes, delay and poll behavior, iteration counts, calls, frame and mask. The callback target is manually installed, so initializer selection is outside scope; operation-4 state is inactive, and no hardware, concurrency, caller reachability, or physical behavior claim is made. `accepted` remains false.
