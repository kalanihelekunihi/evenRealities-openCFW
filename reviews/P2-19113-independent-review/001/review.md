# P2-19113 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x46966A–0x4696FA (144 bytes, 53 instructions); candidate instruction/reference records match exactly. Locked flash SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Verified the ordered fresh `[R4]` calls followed by the `[R4+4]` calls, the 499416 result store at the offset slot, the `MVN` mask yielding 0x00FFFFFF, and the fresh pointer load through literal 0x469BA0 before passing the recorded live arguments. No cache or child semantics inferred.
