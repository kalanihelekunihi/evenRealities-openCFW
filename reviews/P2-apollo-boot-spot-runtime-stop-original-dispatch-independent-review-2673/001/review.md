# Independent review 2673: stop/service with original inactive dispatcher

**Result: PASS_SCOPED.** `accepted` remains false.

All 48 isolated fixtures pass with the dispatcher, operation-4 query, service body, and interrupt helper running original instructions. The supplied table state is zero, so this verifies the inactive query path only. Flag values 2 and 7 select the controlled callbacks; the original common service runs afterward and restores the interrupt mask.

The active state path is separate evidence, not covered by this composition. Callback behavior and physical peripheral effects remain unresolved. No canonical admission.
