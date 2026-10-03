# Independent review 2849 — original predicate/query composition

**Result: PASS_SCOPED.** Source and both body hashes verify, all packet artifact hashes match, and the isolated 1,580-fixture replay passes. I checked the stable-record boolean oracle against the decoded branch sequence: its kind predicate is `kind < 6 || 19 <= kind < 25 || 256 <= kind < 480`, gated by the active record and selected slot.

The replay composes the original predicate and original query leaf, verifies flag-byte writes, query-call selection, return/register/frame/mask behavior, and retains peripheral read traces. It does not assert those traces as an exact oracle. Records are stable in fixtures, so dynamic changes between the predicate’s repeated word reads are not proven. Other memory aliases, hardware behavior, caller ownership, flags, and broader coverage remain unresolved. `accepted` remains false.
