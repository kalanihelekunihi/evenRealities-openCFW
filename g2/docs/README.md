# G2 documentation

Reference documents and per-closure audits. This file says which to read for
what.

## The reference documents

| Document | Answers |
| --- | --- |
| [`source-coverage.md`](source-coverage.md) | *what is compiled from source today?* — the authoritative, function-level record of coverage |
| [`memory-map.md`](memory-map.md) | *where does everything live?* — recovered flash and RAM layout |
| [`upstream-inventory.md`](upstream-inventory.md) | *what is attributable to an upstream, and what is still open?* — the attribution queue and configuration gaps |
| [`linux-reproducible-build.md`](linux-reproducible-build.md) | *how do I reproduce the pinned builds off macOS?* |
| [`transparent-source.md`](transparent-source.md) | *what is every byte of the image made of?* — the Ghidra-to-source pipeline, and what it deliberately does not establish |
| [`transparent-source-ledger.md`](transparent-source-ledger.md) | the measured result of the above, regenerated from the build |
| [`progress.md`](progress.md) | *how did we get here?* — running narrative of the reconstruction |
| [`functional-capability-ledger.md`](functional-capability-ledger.md) | *what functional gaps remain?* — domain-organized gap ledger (protocol, security, platform, health, system, storage, sensors, hardware services, deployment) with per-row status and acceptance gates |
| [`hardware-validation-policy.md`](hardware-validation-policy.md) | *why is physical qualification absent?* — hardware testing is deliberately deferred, and the earlier right-temple “nonresponsive” premise is superseded |
| [`community-source-distribution.md`](community-source-distribution.md) | *how can the community receive and reproduce G2 openCFW without redistributed vendor bytes?* — deterministic bundle, local hydration, and extracted-tree smoke build |
| [`release-licensing-and-redistribution.md`](release-licensing-and-redistribution.md) | *which licenses and redistribution authorities apply?* — live compiled-source inventory and the fail-closed stock-binary boundary |
| [`../tools/analyze_g2_completion_readiness.py`](../tools/analyze_g2_completion_readiness.py) | *what remains before G2 is classified, source-complete, and releasable?* — one byte-conserving, six-component software-only gate (`make completion-readiness`) |

The first four are **SHA-256 pinned** by
`tests/test_runtime_nanopb_decode_svarint_production.py` and
`tests/test_runtime_nanopb_decode_varint32_production.py`. They are evidence
records, not free-form prose; editing one without the matching re-pin turns
those tests red. `progress.md` is not pinned.

## `research/` — per-closure audits

One document per investigated closure, recording what was proven, against which
bytes, and what remains unresolved. These are the bridge between raw evidence in
[`../research/`](../research) and the claims in `source-coverage.md`.

Read them by family — the filename prefix is the subsystem:

| Prefix | Audits | Covers |
| --- | ---: | --- |
| `g2-*` | 236 | first-party G2 subsystems — services, UI pages, drivers, threads, kvdb/nvdb, protobuf handlers |
| `cordio-*` | 73 | the Packetcraft Cordio BLE host — ATT, DM, SMP, L2CAP, HCI, WSF |
| `freertos-*` | 44 | the FreeRTOS kernel boundary — tasks, queues, lists, ports, heap |
| `nanopb-*` | 38 | the nanopb decoder boundary |
| `cmsis-freertos-*` | 23 | the CMSIS-RTOS2 wrapper over FreeRTOS |
| `littlefs-*` | 20 | the littlefs filesystem boundary |
| `easylogger-*` | 13 | the EasyLogger boundary |
| `ambiq-*`, `ambiqsuite-*` | 9 | AmbiqSuite HAL and GPU patches |
| `em9305-*` | 5 | the EM9305 BLE controller |
| others | ~40 | lz4, IAR runtime, TinyFrame, LVGL, CmBacktrace, FreeType, FlashDB, first-party CRCs |

```sh
ls research/cordio-*        # everything proven about the BLE host
ls research/*-candidate-*   # candidates not yet admitted to production
```

Eleven of these audits are hash-pinned by the vendored nanopb and FreeType
verifiers. Treat every file here as an evidence record: append findings, don't
reword history.

## Reading order

New to the tree? [`../README.md`](../README.md) for what the G2 build is. To
share it, start with `community-source-distribution.md`; to audit what remains,
continue with `source-coverage.md` and then a family in `research/` for how a
particular claim was established.

Chasing a specific function? `source-coverage.md` names its closure; the audit
for that closure is `research/<family>-<closure>-*.md`; the analyzer that
produced its evidence is `../tools/analyze_g2_<subsystem>.py`
(see [`../tools/README.md`](../tools/README.md)).

## Related

| Location | Contents |
| --- | --- |
| [`../research/README.md`](../research/README.md) | the raw evidence corpus these audits are built on |
| [`../tools/README.md`](../tools/README.md) | the analyzers that produce the evidence |
| [`../../docs/`](../../docs) | repository-level documentation: layout, build, methodology |
