# Independent review 2735

**Result: PASS_SCOPED.** Static decoding covers exactly 80 original Thumb instructions over `0x428CA4–0x428D90` (236 bytes). Source, body, and candidate artifacts match their hashes. The listing supports the profile calculations/publication, bounded wait and service call, fresh low-seven-bit restore, secondary call, packed return, and frame restore. This map is independently tied to handler9’s source range.

- Wait/service and dynamic behavior are not executed here.
- Bounds, caller ownership, changing reads, and physical effects remain unverified.
- Private evidence only; no canonical admission.
