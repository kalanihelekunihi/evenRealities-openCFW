# Independent review 1855: scoped pass

Status: **PASS_SCOPED**. Accepted: **no**.

## Checks

- Candidate pins and 24 isolated original-instruction fixtures verified; replay JSON matched byte-for-byte.
- Instruction trace confirms direct 7EA4 path when context flag is set or capacity<=physical width. Otherwise it reads capacity bytes to a 512-byte stack buffer, rereads capacity/address remainder, clears the low two remainder bits for the patch offset, copies physical width, then calls 7EA4 on the base.

## Limits

- The synthetic read callback initializes the temporary buffer even while returning nonzero; 7EA4 remains controlled. Capacity above512, wrapped/zero capacity, callback mutation and physical writes are unresolved. No canonical admission.
