# Firmware cutting and retained segments

`firmware_cut.py` splits each official payload into an ordered, gap-free list
of regions, then reassembles it and checks the SHA-256 against the locked
target. Regions that cannot yet be rebuilt from source are carried as
**retained** segments cut from the official image. Each one names its
blockers from [`../../MISSING-TOOLCHAIN.md`](../../MISSING-TOOLCHAIN.md).
A payload can therefore be rebuilt piece by piece while the blocked pieces
are pulled forward as binary. Retained segments never count toward source
completeness.

```sh
python3 tools/cutting/firmware_cut.py verify              # reassemble all payloads byte-identically
python3 tools/cutting/firmware_cut.py report              # retained bytes per payload and per blocker
python3 tools/cutting/firmware_cut.py cut --out build/cut # write every segment to disk
python3 tools/cutting/firmware_cut.py verify --source-dir build/rebuilt   # with rebuilt regions
```

## Manifests

Each manifest in [`manifests/`](manifests) covers one payload with regions in
file-offset order. A region has these fields:

- `label`, `start`, `end`: a half-open byte range in the payload file.
- `state`, one of:
  - `retained`: cut from stock, and must name one or more `blockers`;
  - `source`: bytes come from `--source-dir/<payload>/<label>.bin` and must
    equal stock;
  - `vendor-binary`: a vendor binary carried by design.
- `note`: optional.

[`seed_manifests.py`](seed_manifests.py) generated the initial manifests from
the recovered payload structure: the touch identity regions, the case byte
accounting, the codec FWPK/BINH map, the EM9305 record package, and the Apollo
preamble. As work progresses, split a region by editing its manifest. When its
bytes come from a rebuild, switch it to `source`. `verify` then proves the
rebuilt bytes and the rest of the image still reproduce the official payload.
