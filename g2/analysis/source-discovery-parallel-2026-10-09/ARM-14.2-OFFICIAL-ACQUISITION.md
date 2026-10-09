# Official Arm GNU 14.2.rel1 acquisition metadata

Observed 2026-10-09 through ordinary Chrome browsing. Arm's download page redirected to the official GitLab release listing, which loaded normally without CAPTCHA interaction. Expanded the x86_64 Linux download table. No challenge was solved or bypassed.

Listing: https://gitlab.arm.com/tooling/gnu-toolchains-for-arm/-/tree/releases/14.2.rel1?ref_type=heads

Listing branch commit observed: `ae6adf750d347d0233418fba02bed493ddf4b31a`.

Archive link copied from the visible official listing:
https://gitlab.arm.com/api/v4/projects/tooling%2Fgnu-toolchains-for-arm/packages/generic/gnu-toolchain/14.2.rel1/arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-eabi.tar.xz

Checksum link copied from the same row:
https://gitlab.arm.com/api/v4/projects/tooling%2Fgnu-toolchains-for-arm/packages/generic/gnu-toolchain/14.2.rel1/arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-eabi.tar.xz.sha256asc

The checksum URL was fetched with curl --fail --location into `arm-14.2.rel1-x86_64-arm-none-eabi.sha256asc`. The final response is 122 bytes of plain checksum text, despite the .sha256asc filename. No cryptographic signature verification is claimed.

Published archive SHA-256:
`62a63b981fe391a9cbad7ef51b17e49aeaa3e7b0d029b36ca1e9c3b2a9b78823`

Local checksum receipt SHA-256:
`0058e16f204afcb764a38af718b835e1b3f86e52aef1d0518c8f4397df69b2a7`

The compiler archive was not downloaded or executed by this track. This closes the official URL/checksum discovery blocker; archive integrity and compiler experiments remain owner work.
