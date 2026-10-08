# P2-19115 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x4696FA–0x46976A (112 bytes, 40 instructions), with candidate instruction/reference records matching exactly against locked image SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Confirmed R5 is replaced by the literal, the two full child results are forwarded in order, and the fixed R3=32 argument is supplied as recorded. The base pointer and offset +4 are reloaded before separate calls that store full results at +16 and +20. Each subsequent child uses a fresh reload after the prior calls; no cached value or resource semantics is inferred.
