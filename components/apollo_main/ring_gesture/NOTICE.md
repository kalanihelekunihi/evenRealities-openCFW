# Ring gesture overlay provenance

`ring_gesture.c` is derived from
[`jimrandomh/g2flash`](https://github.com/jimrandomh/g2flash),
`patches/gesture_fwd.c`, pinned at commit
`6d5c58598e047ca5980065a9ee7570ce2d172ca7`.

Upstream author: James Babcock and g2flash contributors.

Upstream license: GNU General Public License version 3 only. This component
retains that license, its source carries an SPDX identifier, and the complete
license text is included in `LICENSE`. The remainder of `openCFW` is kept as a
separable build/aggregation layer; do not assume the license of this component
applies to vendor blobs or grants permission to redistribute them.

The openCFW integration changes the placement model to a standalone 160-byte
overlay, uses manifest-derived Apollo payload offsets, and generates only two
reviewed branch redirects. It intentionally does not bring in the unrelated
image-compression or wake-lease patches.
