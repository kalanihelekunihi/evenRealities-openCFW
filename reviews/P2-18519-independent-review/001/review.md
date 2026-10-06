# Independent review P2-18519

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 86-byte span `0x460B12..0x460B68`; instruction/reference manifests match. This branch is entered only from the bit-1-set path. It resets R8 to 52, computes the destination field pointer, calls `0x460084`, then `0x45FFFE` with the full earlier result and a separately computed field pointer. It freshly reads byte at destination record +40 into SP16, then replaces R8 with `low32(52*R7)` and reads word at destination base + offset +48 into SP12. It stores the full selector at SP8, literal at SP4, and 429 at SP0 before calling `0x43D574`.

The field reads are fresh and follow the lookup calls. R8 retains the offset at span end; the other bit branch bypasses the reset in this region. The next shared join at `0x460B68` is excluded. Local stack writes are not saved-register slots. Child contracts and subsequent body behavior remain unresolved. Partial/unaccepted only.
