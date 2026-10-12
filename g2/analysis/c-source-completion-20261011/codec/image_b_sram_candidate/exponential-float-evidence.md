# Image-B native float exponential source

Native `0x100109c0..0x10010b93` in `binh_b_stage2.bin` SHA256 `d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941` follows Sun fdlibm `e_expf.c` branches and five polynomial coefficients. Pinned primary source is Android bionic commit `a27d2baa`, blob `4e06556b9377ccd3b700e83ad869ba8122b077e6`, saved as `upstream-android-a27d2baa-e_expf.c`, SHA256 `fc0ee2870a217f136780fe785dd296bac947336b3ba59f0cfd75c84d775efcce`. Its Sun copyright and permission notice are preserved in the adapted C.

The native pool at `0x10015598` supplies reduction constants `0x3f317180`, `0x3717f7d1` and signs; the native five polynomial words are `0x3e2aaaab`, `0xbb360b61`, `0x388ab355`, `0xb5ddea0e`, `0x3331bb4c`. The C source encodes these typed floats and uses native threshold words. 100,000 seeded finite host inputs in [-80,80] matched host libc `expf` within one ULP (90,140 exact, 9,860 one ULP). This is numerical and source attribution evidence, not native C-SKY FPU flag proof.

Coherent CK804EF build: `build-exponential-float-round/receipt.json`, 137 units, linked SHA256 `c86e3789f67fb24b7d8125e0c1407e7c42daa2c5363d0076382e839cd57f7050`; 7 true imports. Address catalogue crosswalk is now 199/288; 89 entries remain outside. Binary64 exp at `0x1000f84c` has a distinct helper-heavy body and remains unimplemented; its Ghidra pseudocode loses the double return/call ABI, so no generic host `exp` substitution was made.

The exact primary source is also pinned at `third-party/upstream/android-bionic-fdlibm-a27d2baa/libm/src/` as a Git submodule at commit `a27d2baa0c1a2ec70f47ea9199b1dd6762c8a349`; both downloaded source copies match the submodule byte-for-byte. See `android-fdlibm-submodule-receipt.json`.
