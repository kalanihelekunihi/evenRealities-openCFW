#!/usr/bin/env python3
"""Verify the pinned EasyLogger upstream snapshot and provenance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROVENANCE_PATH = HERE / "PROVENANCE.json"
EXPECTED_REPOSITORY = "https://github.com/armink/EasyLogger.git"
EXPECTED_COMMIT = "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24"
EXPECTED_TREE = "dc9ceb7202c5dd2d58e5e5a9b408b1c05a5ec4f3"
EXPECTED_VERSION_COMMIT = "a607e1715b83d42b2d431e4e415263b7044e0ecb"
EXPECTED_VERSION = "2.2.99"
EXPECTED_SOURCE_EQUIVALENT_COMMITS = [
    "cd93d9c768415f4b7279f2d3ef2366ce15ea087c",
    "34cc1717825c799979a1b4b3739be1e5668a7322",
    EXPECTED_COMMIT,
]
EXPECTED_SOURCE_EQUIVALENT_BLOBS = {
    "easylogger/src/elog.c": "b3a00e3927edf97013ddfffeb157be5c1462a6b4",
    "easylogger/src/elog_utils.c": "165d855d2c8e8470b3543380ca6064c0799a8a44",
    "easylogger/inc/elog.h": "adde47c2df84ea40e4a876f02557c7a4801e8c03",
    "easylogger/inc/elog_cfg.h": "0b4481ed49de06e310e72f4ba53bd5871d0e1722",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"EasyLogger snapshot verification failed: {message}")


def verify_provenance() -> dict:
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    require(provenance["schema_version"] == 1, "unknown provenance schema")
    require(provenance["component"] == "EasyLogger", "component name changed")
    require(provenance["license"] == "MIT", "license identifier changed")

    upstream = provenance["upstream"]
    require(upstream["repository"] == EXPECTED_REPOSITORY, "repository changed")
    require(upstream["selected_ref"] == "refs/heads/master", "selected ref changed")
    require(upstream["selected_commit"] == EXPECTED_COMMIT, "commit pin changed")
    require(upstream["selected_tree"] == EXPECTED_TREE, "tree pin changed")
    require(
        upstream["github_commit_verification"]
        == {"verified": True, "reason": "valid"},
        "recorded GitHub commit verification changed",
    )
    require(
        upstream["observed_remote_head"] == EXPECTED_COMMIT,
        "observed remote HEAD changed",
    )
    require(upstream["declared_version"] == EXPECTED_VERSION, "version changed")
    require(
        upstream["version_introduced_commit"] == EXPECTED_VERSION_COMMIT,
        "version-introduction commit changed",
    )
    require(
        upstream["official_version_tag"] is None,
        "2.2.99 must not be represented as an official tag",
    )
    require(
        upstream["tags_observed"]
        == {
            "2.0.0": "d56a991170857bf0b39930c6c7790e54df4cee8e",
            "2.1.0": "4ba5a626fc25a22695142ff35d2fa23394c15cc5",
            "2.2.0": "980eac7383e26a98837a6b42e9cefcd219b15166",
        },
        "authenticated tag inventory changed",
    )
    require(
        upstream["release_tags_observed"] == ["2.2.0", "2.1.0", "2.0.0"],
        "authenticated GitHub release inventory changed",
    )
    selection = provenance["selection"]
    require(
        selection["source_equivalent_earliest_commit"]
        == EXPECTED_SOURCE_EQUIVALENT_COMMITS[0],
        "source-equivalent lower bound changed",
    )
    require(
        selection["source_equivalent_commits"]
        == EXPECTED_SOURCE_EQUIVALENT_COMMITS,
        "source-equivalent commit set changed",
    )
    require(
        selection["source_equivalent_core_blobs"]
        == EXPECTED_SOURCE_EQUIVALENT_BLOBS,
        "source-equivalent core Git blobs changed",
    )
    require(
        selection["source_equivalence_audit"]
        == "docs/research/easylogger-version-audit.md",
        "source-equivalence evidence path changed",
    )
    return provenance


def verify_files(provenance: dict) -> None:
    seen_paths: set[str] = set()
    for entry in provenance["files"]:
        relative_path = entry["vendored_path"]
        require(relative_path not in seen_paths, f"duplicate file {relative_path}")
        seen_paths.add(relative_path)

        data = (HERE / relative_path).read_bytes()
        require(len(data) == entry["vendored_size"], f"{relative_path} size changed")
        require(
            sha256(data) == entry["vendored_sha256"],
            f"{relative_path} differs from its pinned vendor snapshot",
        )

        if entry["byte_identical"]:
            require(
                entry["upstream_size"] == entry["vendored_size"],
                f"{relative_path} identical-size declaration is inconsistent",
            )
            require(
                entry["upstream_sha256"] == entry["vendored_sha256"],
                f"{relative_path} identical-hash declaration is inconsistent",
            )
        else:
            require(
                data.endswith(b"\n") and not data.endswith(b"\n\n"),
                f"{relative_path} lacks its one documented terminal LF",
            )
            upstream_bytes = data[:-1]
            require(
                len(upstream_bytes) == entry["upstream_size"],
                f"{relative_path} normalized upstream size changed",
            )
            require(
                sha256(upstream_bytes) == entry["upstream_sha256"],
                f"{relative_path} is not upstream bytes plus one LF",
            )

    expected_paths = {
        "LICENSE",
        "src/elog.c",
        "src/elog_utils.c",
        "src/elog_async.c",
        "inc/elog.h",
        "inc/elog_cfg.h",
        "port/elog_port.c",
    }
    require(seen_paths == expected_paths, "snapshot file inventory changed")
    require(
        not (HERE / "src" / "elog_async_api.c").exists(),
        "downstream-only elog_async_api.c was incorrectly attributed to upstream",
    )


def verify_content_markers() -> None:
    header = (HERE / "inc" / "elog.h").read_text(encoding="ascii")
    config = (HERE / "inc" / "elog_cfg.h").read_text(encoding="ascii")
    async_source = (HERE / "src" / "elog_async.c").read_text(encoding="ascii")
    license_text = (HERE / "LICENSE").read_text(encoding="ascii")

    require(
        f'#define ELOG_SW_VERSION                      "{EXPECTED_VERSION}"' in header,
        "elog.h does not declare the pinned version",
    )
    for marker in (
        "#define ELOG_LINE_BUF_SIZE                       1024",
        "#define ELOG_FILTER_TAG_LVL_MAX_NUM              5",
        "#define ELOG_COLOR_ENABLE",
        "#define ELOG_ASYNC_OUTPUT_ENABLE",
    ):
        require(marker in config, f"upstream configuration lost {marker!r}")
    require(
        "size_t elog_async_get_line_log(char *log, size_t size)" in async_source,
        "official async API marker is missing",
    )
    for fragment in (
        "Copyright (c) 2015-2019 Armink (armink.ztl@gmail.com)",
        "Permission is hereby granted, free of charge",
        "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND",
    ):
        require(fragment in license_text, f"MIT license lost {fragment!r}")


def main() -> None:
    provenance = verify_provenance()
    verify_files(provenance)
    verify_content_markers()
    print(
        "EasyLogger 2.2.99 source-equivalent official snapshot, bounded "
        "commit set, MIT notice, and file hashes: OK"
    )


if __name__ == "__main__":
    main()
