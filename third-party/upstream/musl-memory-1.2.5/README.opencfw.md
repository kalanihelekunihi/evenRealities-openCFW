# Pinned musl memory/string source subset

Original upstream: https://git.musl-libc.org/git/musl
Mirror used for file retrieval: https://github.com/ifduyue/musl
Version: v1.2.5, commit `0784374d561435f7c787a555aeab8ede699ed298`.
The primary and mirror Git remotes resolved the tag to the same commit.
`provenance.json` records each unchanged upstream path, retrieval URL and hash.
`COPYRIGHT` retains the upstream MIT license and attribution.

This subset contains only memcpy, memset, strcmp and strlen. It is an attributable
C provider candidate for R1 reconstruction, not original Arm runtime source,
proof of the original dependency version or stock instruction identity.
The R1 builder uses a target-compiler endian macro bridge instead of musl's
complete platform headers; the function bodies remain unchanged.

For an upstream improvement, select and record an explicit new commit,
preserve the old baseline, update per-file hashes and attribution, then rebuild
and rerun runtime plus board/consumer differential checks. Do not silently
advance this pin. The retained license applies to redistribution of this subset.
