# G2 bootloader `sched_hiprio` source closure (`0x004240AA`–`0x00424120`)

Status: production-routed exact dual-profile source; physical validation is
blocked by unavailable physical evidence.

## Authenticated boundary

The official `ota_s200_bootloader.bin` span is 118 bytes at
`[0x004240AA, 0x00424120)` with SHA-256
`dfbd51c61eba1ea51418a1faeaaa99df5aebb0ea900ed157a0c3a55a7b28d144`.
Its sole direct caller is `0x00425F92`. The target body has three direct calls:

- `+0x08` to the retained PRIMASK critical-save entry at `0x0041B8EC`;
- `+0x28` to source-owned `mspi_cq_pause` at `0x00423FB8`;
- `+0x64` to source-owned `program_dma` at `0x0042403E`.

The body loads the authenticated `0x40060000` MSPI base literal at
`0x00424BD8`. Its state accesses establish module `+0x04`, transaction
interrupt `+0x24`, high-priority-active flag `+0x83C`, and pending-entry count
`+0x840`. Register accesses establish `INTEN +0x200`, `INTCLR +0x208`, and the
DMA-complete bit `0x40`.

The behavior and layout match AmbiqSuite 5.1.0 `sched_hiprio`: pending work is
incremented inside the PRIMASK critical section; CQ pause, interrupt setup, and
DMA programming occur only for an empty-to-nonempty transition; pause and DMA
errors are returned unchanged.

## Source and production proof

The BSD-3-Clause candidate is
`research/admission/bootloader_mspi_sched_hiprio_4240aa/`. Its host path uses
ports for critical-section, CQ, MMIO, and DMA effects. Tests cover exact effect
order, both short-circuit paths, the nonempty fast path, state commits, token
restoration, and unsigned pending-count wrap.

The target path emits 118 unrelocated bytes with SHA-256
`8a686489b87dfe77a19e92ea48ec29bd7fe728a8f7d54a94d4f44939520a83e0`
under both reviewed compiler profiles. Applying the three authenticated
`R_ARM_THM_CALL` relocations produces the official span byte for byte.

Production source
`components/bootloader/core_overlay/runtime_mspi_sched_hiprio_4240aa.c` is
registered as an exact in-place leaf. The component build reports 25,869
source-owned bytes, including 10,282 exact in-place bytes, and 121,427 retained
official bytes. The next sequential frontier is AmbiqSuite
`mspi_device_configure`, 1,902 bytes at `[0x00424120, 0x0042488E)` with SHA-256
`3b95c5af6c3c2140cc4e1522a1f284ae31825e4e35ae6c2427e0edba41774818`.

Run:

```sh
python3 -m unittest tests.test_analyze_g2_bootloader_mspi_sched_hiprio_4240aa
python3 tools/analyze_g2_bootloader_mspi_sched_hiprio_4240aa.py
```

## Physical evidence gate

This software-only source wave performed no flash, reset, signing, or MMIO
operation. Live PRIMASK, command-queue, DMA, interrupt, concurrency, and
cold-boot qualification is blocked by unavailable physical evidence. This source closure
does not by itself declare firmware functional completeness.
