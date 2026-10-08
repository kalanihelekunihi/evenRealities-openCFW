# Bounded licensed reference snapshots

These source/header reference materials were recovered byte-for-byte from local Git commit `c618f7f1062624666501152ea215b2e49d824659` using a read-only `git archive` stream. They are not initialized production submodules and are not wired into any firmware build.

- `ambiq-lvgl-backend/` contains only the exact upstream `src/draw/ambiq` subtree (16 files), its MIT license, original G2 source note and source-provenance manifest. G2 runtime/compatibility providers were excluded.
- `liblc3/` contains the complete 42-file historical G2 reference snapshot, including Apache-2.0 license, `PROVENANCE.json` and `SNAPSHOT.sha256`. The upstream file manifest covers 38 source/project files.
- `nema-sdk-headers/` contains the 33-file headers/GPU-extension snapshot, its Think Silicon header license, README and historical provenance record. Vendor archive binaries and executable artifacts were excluded.

`REFERENCE-SNAPSHOT-MANIFEST.json` records historical Git tree and blob identities, byte sizes and SHA-256 values. All 91 package-tree files and four ancillary license/provenance files match their historical Git blob IDs. All 38 LC3 upstream manifest entries and all 16 Ambiq backend source-provenance entries also verify. The Nema snapshot is header/interface material; it does not provide complete proprietary Nema C implementation.

Retain each package's original license and provenance when inspecting or sharing these snapshots. Their presence here does not prove that the locked firmware was produced from these exact public snapshots or compiler outputs.
