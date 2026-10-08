# P2-20909 independent review

Status: **partial / unaccepted**.

Fresh replay passed for the 16-byte slice at 0x47D9B4..0x47D9C4 from the pinned image (SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`). Candidate data hash and independently replayed data hash both equal `7f8c8c37bc4fcdd642b5d1b1feeba67d25acae53565d7402537f4e350d8af14b`; the extracted bytes agree exactly. The four little-endian words are 0x00730CFC, 0x00774774, 0x00711C64, and 0x0078EDF4.

All four words have a mapped PC-relative LDR consumer. Recomputed aligned-PC displacements agree with the recorded addresses: loads at 0x47D82A, 0x47D832, 0x47D84E, and 0x47D874 reference 0x47D9B4, 0x47D9B8, 0x47D9BC, and 0x47D9C0 respectively. Each consumer is present in the referenced map component; the evidence supports these references, not pointed-to string/template ownership or exhaustive firmware coverage.

The candidate receipt retains `accepted: false` and `status: partial`; no source or gate files were changed.
