# Independent review 2823 — handler 0 early chain

**Result: PASS_SCOPED.** The corrected handler0 body hash matches `0x427E84..0x42805A`; source and candidate artifact hashes also match. The isolated 16-fixture replay passes with original instructions through the secondary helper, high-target restore, runtime stop, inactive operation-4 path, and flag handling.

The modeled path is limited to same-index selection with runtime control bit 0 set and inactive zeroed op4 state. The replay checks the ordered writes, absence of delays, packed return, and frame/register/mask preservation. Other index relationships, secondary categories, active op4 state, hardware effects, concurrency, and canonical admission are outside scope. `accepted` remains false.
