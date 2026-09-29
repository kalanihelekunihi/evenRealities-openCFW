# macOS C-SKY compiler backport

`gcc-safe-ctype.patch` is the unmodified patch for upstream GCC commit
[9970b576b7e4ae337af1268395ff221348c4b34a](https://gcc.gnu.org/pipermail/gcc-cvs/2024-March/399600.html),
by Francois-Xavier Coudert, signed off by Dimitry Andric, 2024-03-07.
It retains the upstream GCC source licensing (GPL), not the MIT license of
our Python build driver. The patch moves C++ standard headers before
`safe-ctype.h` to prevent macro poisoning with recent libc++ headers.

The patch applies unchanged to C-SKY GCC revision
`1e9b70447a8417f5c692370de4533e43d754e8fa` (13.0.1). The build driver verifies
the patch and both the original and resulting `gcc/system.h` SHA-256 hashes.
An already-applied authenticated patch is accepted; unexpected changes stop
the build. This is a host compiler build fix, not a firmware behavior change.

Build with `python3 g2/tools/build_g2_csky_macos.py`. Sources must first be
fetched at the revisions pinned in that driver. The recipe uses Apple Clang,
macOS system zlib, and existing Homebrew GMP/MPFR/MPC. It installs only under
`g2/build/csky-macos/install`. No Linux environment is involved. Target libc,
libgcc, and complete firmware qualification are separate from this compiler
build.
