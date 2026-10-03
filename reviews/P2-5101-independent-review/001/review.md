# Independent review P2-5101

**Status:** PASS_SCOPED  
**Accepted:** false

Source hash and isolated replay pass. Guards, classification/allocation routing, metadata and block helper call order, and the documented path-dependent return registers agree with the exact instruction body and literal references. The map does not claim successful allocator semantics beyond the decoded caller/callee boundaries.

## Limits

Assertions can return and child effects remain separately scoped. No allocator-wide behavior, hardware, C implementation, or admission claim. Private partial evidence; accepted:false.
