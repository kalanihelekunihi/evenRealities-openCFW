# P2-20727 independent review

Status: **partial / unaccepted**.

Fresh replay passed against the locked image. Image SHA-256 and source/fresh receipt hashes verified.

24B tail; exact byte48==1 condition calls 479B74 then 47B730 unconditionally; exact mismatch returns the fresh byte48 value. Shared epilogue discards 72 local bytes and saved R3, then returns live second-helper R0 or mismatch byte.

No whole-firmware coverage or helper contracts are inferred. No source or gate files were changed.
