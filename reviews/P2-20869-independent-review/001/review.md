# P2-20869 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 78 bytes at 0x47D08C..0x47D0DA; pinned image/source hashes and tiling match. The 40-byte frame is inherited. Diagnostic paths make separate status queries, with the mask setup using live R3 without a local assignment. The later functional path calls 0x45A568 first, then freshly loads buffer byte4, compares its full byte value against the helper LOW8 result, and branches to distinct pending targets. No earlier helper result or byte observation is reused.
