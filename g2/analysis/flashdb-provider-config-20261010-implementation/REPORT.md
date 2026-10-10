# FlashDB provider configuration constraint

Pinned official FlashDB 2.1.1 source commit: `714d6159e7e6afb267a3953756abca445c350e61`. Exact fetched source/header URLs and hashes are in the two source receipts. Original ranges are checked directly against the locked raw image, SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`; see receipts.json.

## Immediate result

Ten successful ARM32 Thumb compile probes (Apple clang, Cortex-M4 layout target, default versus short enums, all five supported write granularities) establish independent constraints under these pinned sources:

* Stock `get_kv` at **0x5444F4** allocates an 88-byte KV object, reads value_len at +12 and addr.value at +84. Short enums match all three; default enums produce 92/+16/+88. This independently supports the prior 2220-byte database stride result rather than assuming cache sizes establish enum width.
* Stock `write_kv_hdr` at **0x5445B2** calls status provider **0x5858D8** with status count 6, pre-write status 1 and sync=false. On zero status result it calls flash-write provider **0x585A52** with address+4, header+4, count=20 and sync=false. A nonzero status result suppresses that second call. Both results are narrowed to an unsigned byte.
* Pinned FDB_STATUS_TABLE_SIZE and unchanged kv_hdr_data definition give magic offsets **4,8,20,40,80** for FDB_WRITE_GRAN **1,8,32,64,128** respectively. Only granularity 1 matches the stock +4. Transfer counts are **20,20,20,24,32**: count 20 alone does not discriminate 1 from 8 or 32. The discriminating constraint is the offset.
* Stock public get-blob provider **0x54454A** checks parent init_ok at +24, invokes optional lock/unlock at +28/+32, and calls get_kv with blob.buf, blob.size and &blob.saved.len (+16). The pinned FAL-mode candidate matches these parent offsets.

## Evidence and boundaries

`probe.c` includes the exact pinned low-level/public headers and the unchanged disk-header struct extracted from pinned fdb_kvdb.c. Each variant retains its config, object, raw constants, compiler command and diagnostics. `probe-results.json` labels every emitted constant. `reproduce.py` rebuilds the matrix and re-verifies every original-byte receipt. No guest runtime fixtures were run in this continuation. GNU disassembly and ARM compiler layout are the evidence; these are source/configuration constraints, not instruction-byte equality or physical flash/bus behavior.

The provider get_kv returns min(requested size, recorded value size), writes recorded size when the output pointer exists, and ignores the flash-read return. Missing keys return zero and clear that output. This is a static binding to the pinned private get_kv body; find_kv and flash providers remain unvalidated here.

The 64/64 cache candidate gives database size 2220 with short enums, but this report does not independently establish those cache counts. Different cache-count combinations can yield the same stride. Name-buffer alignment also leaves nearby name limits indistinguishable from the sampled field offsets. File-mode/FAL alternatives and complete production compiler/link configuration are outside this ten-probe matrix. TSDB macro state, provider implementations, full database behavior and byte-identical rebuild remain open. No production source, reference payload, device, Git index or submodule pin was changed.
