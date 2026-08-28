# Ring gesture overlay provenance

`ring_gesture.c` is a modified derivative of
[`jimrandomh/g2flash`](https://github.com/jimrandomh/g2flash),
`patches/gesture_fwd.c`, at commit
`6d5c58598e047ca5980065a9ee7570ce2d172ca7`. It is not a byte-identical copy.
`upstream/gesture_fwd.c` retains the exact 4,029-byte upstream blob, and
`DERIVATION.patch` records every change between that blob and the checked-in
OpenCFW source.

`PROVENANCE.json` retains the complete Git commit payload plus every entry of
the root and `patches` trees. `verify_provenance.py` reconstructs those objects
and proves the following offline chain:

`6d5c585...` -> root tree `5509f7a...` -> `patches` tree `a6dd12f...` ->
`gesture_fwd.c` blob `4997b81...`.

The historical commit has no embedded signature. The object proof therefore
authenticates the commit/path/blob relationship and exact bytes, but it does
not independently authenticate GitHub account control or assert that the
OpenCFW derivative is identical to upstream. The repository attribution is the
recorded provenance claim; verification is deliberately local and performs no
fetch, checkout, DNS lookup, or other network access.

Upstream author: James Babcock and g2flash contributors.

Upstream license: GNU General Public License version 3 only. The root tree binds
the upstream `LICENSE` blob `e72bfdd...`; the complete text included here as
`LICENSE` is that exact 35,148-byte blob with one terminal LF added. This
component retains that license and its modified source carries an SPDX
identifier. The remainder of `openCFW` is kept as a separable build/aggregation
layer; do not assume the license of this component applies to vendor blobs or
grants permission to redistribute them.

The openCFW integration changes the placement model to a standalone 160-byte
overlay, uses manifest-derived Apollo payload offsets, and generates only two
reviewed branch redirects. It intentionally does not bring in the unrelated
image-compression or wake-lease patches.
