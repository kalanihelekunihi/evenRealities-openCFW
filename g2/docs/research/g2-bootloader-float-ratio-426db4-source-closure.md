# G2 bootloader floating ratio source closure

The authenticated stock entry is `[0x00426DB4,0x00426EAC)`, 248 bytes,
SHA-256 `4082869f6c1884fe571d7d8335b2fc32ee6326cfb02b78d01f07c1da5bacc3dd`.
Its sole caller at `0x00426FC8` supplies output pointers in `r0`/`r1` and
floating inputs in `s0`/`s1`. The helper normalizes through the source-routed
common-divisor function, applies a one-ULP integer tolerance, scales
denominators below four, and accepts a numerator of `1..63` and denominator
of `4..960`. Its retained edges are two `fmodf` and four `roundf` calls. The
Apollo-main analogue at `0x005393E8` agrees in 230 of 248 bytes; differences
are address-coupled calls.

`runtime_float_ratio_426db4.c` is 2,629 bytes of clean-room MIT C, SHA-256
`8ef644572cc18f6bf5b9ad732af0549e6ee8f59abcc935f01adb218910d27642`.
Its pointer-first signature and `pcs("aapcs-vfp")` preserve the mixed
core-register/VFP ABI. Apple clang 21.0.0 and Homebrew clang 22.1.8 emit the
same 252-byte leaf. Its unrelocated SHA-256 is
`da4c93662605a83943051f4f8385c2e2d767a0bcecfd5789eb732c0c3fb39156`;
after seven strict relocations its SHA-256 is
`cd5568ffb4c2c273bf85947cf4aa4fdf8441eba18c6a3b5d16e59b1340f086e3`.
It occupies `[0x00415CD4,0x00415DD0)`, and the stock entry is a generated
`B.W` plus NOP fill.

Current deterministic Apple/Linux provider hashes are
`ac373b3c0caa5dcb6ae25cf6f004c76e778d936b7a584e3ecdf83a17283bca36`
and `4993c8d06b148fa4518268af8fd5133e1494f18c74387249326dac78da1ddde0`.
Complete package hashes are
`12a36be93bc410f2e9e122343455b24888b3750c3c0888a4410aa46cf983b891`
and `a17eb8cb3527d7956c9da71f450488a0e19e08d3862e4753ec62d1ffaf4472af`;
both have zero unresolved flash regions.

No signing, flashing, reset, MMIO access, or physical-device operation was
performed. Target ABI behavior, timing, caller integration, and cold boot are
blocked by unavailable physical evidence. Firmware-wide completeness is not
claimed.
