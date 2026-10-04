# P2-9047 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All mapped instruction bytes match the pinned image and all literal references resolve exactly.
- The active-record lookup checks the halfword key against 0xFFFF and a separate fresh activity byte at +22, returning the first qualifying record among up to three stride-28 candidates. The wrappers truncate their input to low16 and return saved entry R7 rather than the child result.
- The accounting routine first calls 53013C; on nonzero child result it increments record+25, then conditionally decrements global+130 using a separate fresh reload. It returns 1 on this path and 0 on child-zero path.

Limitations:

- Child 53013C purpose and side effects are unresolved. Fresh reloads mean observed values may differ under mutation; no atomic/concurrency or ownership claim is supported.
