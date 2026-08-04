# Armink EasyLogger 2.2.99-labeled snapshot

This directory contains the minimal official EasyLogger core, async reference,
headers, configuration template, port template, and MIT license needed to
develop the Apollo-main source replacement. The selected source is pinned to
commit
[`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`](https://github.com/armink/EasyLogger/commit/a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24)
of the primary
[`armink/EasyLogger`](https://github.com/armink/EasyLogger) repository.

## Version and tag qualification

The upstream repository does **not** have a `2.2.99` tag or GitHub release.
Its public tags end at `2.2.0`. Commit
[`a607e1715b83d42b2d431e4e415263b7044e0ecb`](https://github.com/armink/EasyLogger/commit/a607e1715b83d42b2d431e4e415263b7044e0ecb)
changed `ELOG_SW_VERSION` from `2.2.0` to `2.2.99` on 2019-11-30, and later
master commits continued to report `2.2.99`. The selected commit is the
latest official master commit observed during authentication and gives this
tree a stable, reproducible upstream identity. It does not prove which one of
the many `2.2.99`-labeled master revisions Even used.

Focused comparison against the G2 core establishes a smaller
source-equivalent set. The argument-aware directory/function/line helpers
introduced by commit
`cd93d9c768415f4b7279f2d3ef2366ce15ea087c` are present in the firmware.
That commit and the only two later official master commits, `34cc171` and the
selected `a596b264`, have identical `elog.c`, `elog_utils.c`, `elog.h`, and
`elog_cfg.h` Git blobs. The stripped firmware cannot distinguish
documentation-only commits, so `a596b264` is the reproducible vendoring pin
for this exact source-equivalent core, not a historical-checkout claim. See
`docs/research/easylogger-version-audit.md`.

`PROVENANCE.json` records the repository, commits, observed tags, file sizes,
and both upstream and vendored SHA-256 hashes. GitHub's commit API reports the
selected commit signature as verified (`reason: valid`).

## Apollo-main file qualification

The official snapshot provides:

- `src/elog.c`
- `src/elog_utils.c`
- `src/elog_async.c`
- `inc/elog.h`
- `inc/elog_cfg.h`, the upstream example configuration
- `port/elog_port.c`, the upstream port template
- `LICENSE`, the upstream MIT license

The official repository has never contained `easylogger/src/elog_async_api.c`
in any inspected ref or historical object. That filename is nevertheless
retained in the G2 firmware's build-path strings. It must therefore be treated
as a G2-local file, renamed downstream derivative, or source from another
unproven repository. This vendor tree deliberately keeps the official
`elog_async.c` name and does not fabricate an upstream `elog_async_api.c`.

The upstream async implementation owns a private ring buffer and optional
POSIX worker. Apollo main instead has recovered G2 queue/event behavior and a
255-byte record cap. Do not enable `src/elog_async.c` in the firmware merely
because it is vendored: use it as the API/behavior reference while keeping the
G2 queue and CMSIS/FreeRTOS interaction in a separately reviewed Apollo port
or glue module.

`inc/elog_cfg.h` and `port/elog_port.c` are pristine templates, not the
openCFW G2 configuration or port. The recovered G2 definitions must live
outside this upstream snapshot so the vendor bytes remain auditable.

## Byte preservation

The five core source/header/config files are byte-identical to the selected
upstream Git blobs. Upstream `LICENSE` and `port/elog_port.c` lack a terminal
newline; the vendored copies append one LF and are otherwise identical.
`PROVENANCE.json` includes the upstream hashes and verifies that removing the
single documented LF reproduces them. `.gitattributes` prevents checkout
line-ending conversion.

Run the offline integrity check with:

```sh
python3 openCFW/third_party/easylogger/verify_snapshot.py
```

## License

EasyLogger is distributed under the MIT license. The complete upstream text is
in `LICENSE`, and each vendored source/header/template also retains its
upstream MIT notice.
