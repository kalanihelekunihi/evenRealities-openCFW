# Independent review 1935 — left-clipped overlay traces

**Result: PASS_SCOPED.** Candidate `touch-row-overlay-left-clipping-traces-1926/001`; receipt SHA-256 `24674f34d59669a8cce9e240a794954e69ab6be55f719c35fabf68d8397aa11b`.

Source and all listed artifact pins match. Replaying the immutable script in a unique temporary directory passes all 36 fixtures and reproduces replays.json exactly. Original CRC, provider 4860, and AA2C instructions execute without interception.

With current interval [64,128), the tested overlays cover disjoint and overlapping placements. For a left-starting overlap, the candidate’s model uses source delta 64-(offset mod 64), destination delta zero, and amount overlay_end-64; the original path can copy past the logical right edge. Right-starting overlap uses destination delta offset mod 64 and clips to min(128,overlay_end)-offset. Full 256-byte output, result, and SP are compared.

The backing row is intentionally oversized and bytes beyond its nominal 128-byte length are zero-filled; this supports observing the decoded copy extent, not a valid physical row layout. The current scratch overlay is outside the copied window.

Fixed geometry and synthetic memory only. This is a trace-only clipping branch, not complete routine recovery or proof of valid out-of-row storage. Mirrors, generalized interval behavior, physical storage, concurrency, and canonical admission remain unresolved.
