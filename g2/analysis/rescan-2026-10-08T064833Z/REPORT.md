# OpenCFW rescan — 2026-10-08 06:48 UTC

Compared with the 05:33 UTC scan. Inspection only; this new scan directory is the only output written. No generators, compilation, tests, index changes, commits or device operations. Existing validation receipts were inspected, not rerun. Concurrent work may advance after capture.

## What changed

The previous narrow canonical scope (`g2/components/bootloader` and `g2/components/foundation`) remains **475 C/header/assembly files**, with **0 added, 0 modified, 0 removed**. Of these,384 are tracked/indexed,91 untracked and0 ignored.

There is now an additional canonical **offline** touch source home: [eeprom_offline](../../components/touch/eeprom_offline/README.md) contains11 C/header inputs, and [eeprom_init_offline](../../components/touch/eeprom_init_offline/README.md) contains2. All13 are untracked and none is ignored. The previous scan inventoried only bootloader/foundation and reported touch source under analysis; this expanded scope must not be presented as13 additions to that unchanged475-file baseline. These modules are isolated reconstruction, not integrated production firmware.

- [Read closure](../touch-read-closure-2026-10-08/REPORT.md): reconstructed simple/extended reads and dispatcher; existing receipts record690 native/original read comparisons,1148 history-helper,1728 extended-write and800 complete command7 comparisons. Read coverage is616/620 original instruction bytes; coherent tested geometry does not reach the four-byte row-search exhaustion branch. SROM and storage effects remain synthetic.
- [Initialization closure](../touch-init-closure-2026-10-08/REPORT.md): independent initialization, provider creation and application readiness wrapper;1402 native/original cases and3 rejected negative controls. Reset-copy instructions establish actual factory configuration:256-byte logical capacity, extended mode,wear2,redundancy1,blocking1,128-byte rows/sectors. Main+mirror storage spans0xe400..0xec00 outside the OTA payload. Initialization discards last-row scan status: readiness does not prove saved-record validity.
- SDK attribution advanced to32 selected functions/2864 exact compiled bytes, with producing revision still ambiguous. A separate1402-case SDK/original initialization suite borrows original memory/division primitives. Unmodified Apache-2.0 block-storage1.3.0 source/header/license now exists under [third-party/upstream](../../../third-party/upstream/infineon-block-storage-1.3.0/README.md). Selected byte matches are not whole-image source completeness.
- History closure now has its completed report/provenance/manifest; the prior scan observed C/results before that report was completed.

## Integrity and Git visibility

Fresh hashes match all110 locked audit inputs,291 manifest-listed sealed files across the relevant delivered analysis/canonical/vendor namespaces, and all four previously recorded checkpoints. The sealed-file count expands the previous196-file scope; it is an integrity count, not firmware progress.

Git has6205 indexed additions,25 indexed modifications,4 indexed additions with further working-copy changes, and2868 untracked files at capture. Untracked files increased83 from2785; this includes source, documents and test receipts and is not83 firmware functions.

`git check-ignore -v` finds no match for canonical touch `read.c` or `init.c`. `.gitignore:15:build/` hides `g2/build/` artifacts. No global excludes file is configured; Git lists one worktree. Source visibility still requires an untracked-file view. There is no evidence that .gitignore hides these new source files, and no blanket ignore change is warranted.

## Practical conclusion and remaining gaps

Work now includes actual readable C/header inputs and original-instruction comparisons, rather than only scripts/README/state. Existing accepted checkpoint hashes remain unchanged: this offline touch source has not become a production firmware replacement. Command7 ACK/deferred success still cannot establish durability because installed row adapters discard lower-level flash errors; RAM queries likewise cannot certify persistence.

Bootstrap0x395c, saved-record validation and erase/default recovery remain the next bounded static analysis. No completed bootstrap source/test deliverable exists in this scan. Actual persistent-storage captures and resident SROM implementation or physical traces are needed for hardware durability/timing conclusions. Whole-firmware pseudocode coverage, integrated source completeness and byte-identical OTA reconstruction remain separate and unproven.
