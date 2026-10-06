# Fixture diagnostics

The first full-image matrix attempt mapped all3.5MB for every case and was terminated without a completed result after excessive runtime. Its exact verifier is preserved as full-image-first-verifier.py; no PASS credit.

The first sparse-page fixture failed the unchanged instruction provenance assertion at4c2ffe: a4-byte Thumb BL straddles the4c3000 page boundary. Adjacent executable pages are now represented as one contiguous authenticated span. Guest bytes, matrix and all comparison assertions are unchanged. No completed matrix from this failed fixture is credited.
