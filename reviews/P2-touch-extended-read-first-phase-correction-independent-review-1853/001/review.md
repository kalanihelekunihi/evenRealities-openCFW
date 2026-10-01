# Independent review 1853: first-phase stride correction passes

Status: **PASS_SCOPED**. Accepted: **no**.

The correction binds to original packet 1814/001 and updates only the mirror-stride prose. Original instructions 8420–8430 multiply count and copies, then multiply by `physical_width >> 2` and shift the result left two. The clarified formula is `count * copies * (floor(physical_width / 4) * 4)`.

The first-phase search wording “up to count times” is accurate: the 836A bound check precedes each advance, rejected candidates increment at 8368, and count N can lead to N checks. The separate audit 1834 corroborates this for observed searches.

This does not expand the partial region or add fixtures; no complete-function, physical storage, C implementation, or canonical admission claim is made.
