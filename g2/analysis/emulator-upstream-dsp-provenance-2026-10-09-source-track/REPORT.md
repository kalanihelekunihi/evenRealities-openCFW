# Finite compiler provenance and Pigweed registration review

## New concrete gain

Official NationalChip GX8002 setup documentation names C-SKY Tools V3.10.15 Minilibc abiv2 B20190929, GCC 6.3.0, and the x86_64 archive `csky-elfabiv2-tools-x86_64-minilibc-20190929.tar.gz`. The captured current document and live sharing-link response are hashed in PROVENANCE.json. This resolves the distribution-name/download-location uncertainty in docs/tooling-availability.md without changing that canonical ledger.

Official URL: https://document.nationalchip.com/software/lvp/SDK开发指南/SDK快速入门/搭建开发环境/

The official share http://yun.nationalchip.com:10000/l/HFjTus redirects to a public JavaScript portal shell with HTTP 200. No archive or license was acquired. No downloaded script was executed; portal contents and archive availability remain unverified. The document also explicitly describes the full LVP SDK as a private GitLab release requiring manufacturer authorization. Public lvp_aiot is a comparator, not proof of access to that private SDK.

Existing acquired lvp_aiot pin d4aa00943e22f9ddfa424f979fae3ee2a62f5c0b (https://github.com/NationalChip/lvp_aiot) Makefile 230–241 enforces that exact distribution and CK804ef hard-float flags. Lines 332–333 conditionally add __FPU_PRESENT, UNALIGNED_SUPPORT_DISABLE and CSKY_SIMID; Kconfig 231 defaults the DSP source-build option off and warns that FFT1024/2048/4096 are unsupported. utility/Makefile references utility/libdsp/Makefile, but that referenced file is absent in this acquired tree. Thus the optional source build is incomplete here; do not assume the headers supply a complete build. Headers have Apache-2.0 notices, whereas the top Makefile says NationalChip all rights reserved; license scope is per-file.

The matching archive DWARF reviewed by the other tracks establishes GNU C11 6.3.0 CK804ef hard-float O2 and section flags. The official package name is a narrower candidate, not proof that this precise distribution built the stock bytes. No compiler/build/reconstruction was run. Exact source revisions, table inputs and final linkage remain open.

## Pigweed proposal

Already acquired three HCI schemas and Apache-2.0 LICENSE at immutable e175383a07c5b811a98924fc662d1001f1d220d0 in ../emulator-upstream-fresh-2026-10-09-1810-source-track/references/pigweed-hci/. That provenance receipt includes per-file URLs and hashes, and previously verified HEAD de25dbea944d7d6e11353eb5c4a299ae0e3e7117. No duplicate acquisition was made.

Proposed owner-reviewed registration:

```ini
[submodule "reference/pigweed-hci"]
    path = third-party/reference/pigweed-hci
    url = https://pigweed.googlesource.com/pigweed/pigweed
```

Pin the gitlink to e175383a07c5b811a98924fc662d1001f1d220d0. Full checkout is unnecessary for current schema evidence. No Pigweed registration exists in .gitmodules. Targeted registration can in principle avoid unrelated staged work, but this source track is expressly restricted to its own new output/download directories and forbidden to alter .gitmodules/root index. Therefore no registration was performed. Existing staged R1 acquisitions and all concurrent evidence were left untouched.

## Search closure

Searched the pinned NationalChip SDK build/configuration references, consolidated tooling-availability ledger, official current and migrated NationalChip setup docs, official C-SKY toolchain-build repository search results, and existing pinned Pigweed provenance. Generic newer C-SKY toolchain builds do not establish the 2019 Minilibc distribution. No new source repository download was justified; only the newly useful official setup document and portal response were acquired. Prior HCI bitmap searches were not repeated. Remaining finite lead: inspect the official portal through an authorized workflow to obtain archive metadata/license, then acquire the exact public package if available. Whole-pseudocode/freeze gates still govern any later rebuild.
