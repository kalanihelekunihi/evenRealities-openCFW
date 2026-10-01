# Independent review 1801: scoped pass

The exact helper spans are 810C..812A (30 bytes/15 instructions) and 812A..814C (34/17). The 864 isolated fixtures match wrapped context-derived limits, width rounded down to a multiple of four, unsigned pointer comparison, copies<=1 passthrough, and wrapped alternate-group pointer arithmetic. No calls are made; SP and return behavior match.

All address behavior is numeric arithmetic over synthetic state; no physical row mapping, pointer validity or concurrency behavior is established. No canonical acceptance or coverage change is made.
