# SybilSight G2 CFW 2.2.6.12

This directory defines the SybilSight custom-firmware release `2.2.6.12`. It is built from the authenticated official G2 `2.2.6.10` EvenOTA package because no authenticated official `2.2.6.12` vendor image is present in this repository. The two versions are deliberately recorded separately: `2.2.6.10` is the vendor base and `2.2.6.12` is the SybilSight CFW release identity.

The release is intentionally based on `g2flash` commit `d5eb48dd9dcda4cc630458ec365bc546036678c2`, the last pinned revision before Faceclaw's wake-lease patches, and adds the reviewed mode-10 virtual canvas. It does not install Faceclaw's settings field-101 decoder, either idle-double-tap takeover, or the `even_ai_display_ctrl` trampoline; native “Hey Even” therefore enters the unmodified stock handler. The glasses continue to scan out the proven 576x288 physical framebuffer while CFW holds a 576x480 packed 4bpp backing canvas and exposes rows 0 through 479 by panning the 288-row viewport between `viewportY=0...192`. SybilSight negotiates this path only when the settings response advertises `canvas480`; stock and older CFW use the existing display path.

## Build for review

The builder verifies the vendor package SHA-256, the exact `g2flash` commit, the EvenOTA package identity, all three runtime identity paths (settings, product-test, and inter-lens reporting), and all nine vendor-provenance version strings that must remain unchanged. It also verifies the resulting capability marker, repaired preamble/component checksums, a byte-for-byte replay of the generated patch set, and that all four former Faceclaw hook sites retain their authenticated stock bytes; any output containing the removed `wakelease` capability is rejected. It only writes local artifacts and never downloads firmware or flashes glasses.

```sh
python3 openCFW/releases/g2-2.2.6.12/build.py \
  --g2flash /path/to/g2flash \
  --stock firmware/ota/2026-07-22/g2-2.2.6.10-e28738432d7b612d625331b00383149b.bin \
  --output openCFW/build/g2-2.2.6.12/g2-2.2.6.12-sybilsight-cfw.bin
```

The output directory also receives a replayable `.patches.json` and a `.manifest.json` containing the exact output hash, source-patch hash, release/base identities, capabilities, geometry, and `"flashed": false`. Review those artifacts before using the repository's separate recovery-aware flashing workflow.
