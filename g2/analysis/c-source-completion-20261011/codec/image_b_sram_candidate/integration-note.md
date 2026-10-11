# Image-B SRAM candidate integration

Image-B is a separately loaded GX8002 program with the pinned 82,060-byte
`binh_b_stage2.bin` corpus (SHA-256
`d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941`).
It must have its own C-SKY CK804EF hard-float relocatable result under the
Codec receipt. Do not append its units to image-A's `source_paths` or link its
object into image-A's `candidate.o`.

The reproducible subbuild is:

```sh
python3 g2/analysis/c-source-completion-20261011/codec/image_b_sram_candidate/build.py \
  --output <firmware-c-output>/codec/image-b-sram
```

Its `receipt.json` binds every source and object hash, linked output hash,
architecture, and true undefined symbols. A distinct
`codec.image_b_sram_candidate` receipt field can contain that receipt and the
subbuild command status. `source_complete` and
`data_and_final_layout_complete` must remain `false`. The current selected
subgraph links without imports; image-B reset/data/layout and
135 retained catalogue functions outside this candidate remain unqualified.

The source manifest is the explicit `SOURCES` array in the subbuilder, currently
88 units, including 77 under `g2/components/gx8002/image_b_sram_candidate/` and
11 pinned LLVM compiler-rt sources. It is not a
filesystem glob. The subbuilder uses the same pinned C-SKY toolchain and Docker
image as image-A but compiles and links independently.

Typed flash profile configuration in backup_flash_profile_data.c has a field-level native payload check in flash-profile-data-receipt.json. Its runtime placement under the candidate DRAM mapping remains open.
