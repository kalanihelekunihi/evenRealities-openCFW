# Independent review 1843: scoped evidence pass

Status: **PASS_SCOPED**. Accepted: **no**.

## Checks

- Receipt pins verified; isolated replay passed 48 original-instruction traces and output JSON matched byte-for-byte.
- For deliberately out-of-public-range offsets and all eight current rows, search visits four candidates with no matching logical interval and proceeds with the final stepped pointer. Modeled output slicing, zero status, suffix preservation and SP match.

## Limits

- This is internal malformed-input behavior after bypassing public dispatcher bounds, not a valid public read. Uniform geometry only; wrap, inaccessible rows, concurrency and physical storage remain unresolved. Trace-only, no canonical admission.
