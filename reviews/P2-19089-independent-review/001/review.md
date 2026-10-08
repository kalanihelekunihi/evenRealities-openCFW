# P2-19089 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x46928C–0x46931C (144 bytes; 53 instructions), with instruction/reference records matching exactly. Locked image SHA-256: `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Verified fresh diagnostic mask reads, the full mode-one comparison, and the two independent FULL predicate-result tests. The R4 flag distinguishes the routes: the second ordered 0x464C36 action is reached after either success path; on the R4=1 path, 0x454B4C(500, live args) occurs between the two actions. The literal 500 is an observed argument; no delay behavior is inferred. Saved input remains at SP+16 for the following chunk.
