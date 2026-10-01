# Independent review 1861: scoped pass

Status: **PASS_SCOPED**. Accepted: **no**.

## Checks

- Receipt pins match and 72 isolated fixtures reproduce exactly. Body boundaries exclude alignment and literal; original geometry helper establishes 128-byte rows.
- Original A7CC rejects nonmultiples of 128 with the pinned error; otherwise original 8D50 is called for each 128-byte segment, its result ignored, pointers advance, and an unsigned wrapped end comparison controls loop entry. Misaligned destination is accepted; a wrapped end below start skips the loop.

## Limits

- Only 8D50 is controlled, so command effects are unknown. No physical flash, malformed memory or canonical claim.
