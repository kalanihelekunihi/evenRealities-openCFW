# P2-20687 independent review

Status: **partial / unaccepted**.

Fresh replay passed against the locked firmware image. I verified the image SHA-256, the source receipt file hashes, and the fresh replay receipt hashes; replay also validates the mapped raw bytes and instruction tiling.

382B/147 instructions/18 branches; four components tile 47AB6C..47ACEA.

This review is limited to the artifact and behavior described above. It does not establish whole-firmware coverage, source completeness, or helper contracts. No source or gate files were changed.
