#!/usr/bin/env python3
"""Validate raw unittest logs against durable normalized evidence."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping, Optional, Sequence, Tuple


FORMAT = "openCFW.unittest-regression-evidence"
VERSION = 2
RESOLVER_FORMAT = "openCFW.unittest-skip-resolver-map"
RESOLVER_VERSION = 2
OPENCFW_ROOT = Path(__file__).resolve().parents[1]
RULE = "-" * 70
SEPARATOR = "=" * 70
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}$")
MATCH_BINDING_NODES = tuple(
    node_type
    for node_type in (
        getattr(ast, "MatchAs", None),
        getattr(ast, "MatchStar", None),
    )
    if node_type is not None
)
RESULT_BLOCK_RE = re.compile(
    rf"^(?P<separator>{re.escape(SEPARATOR)})\n"
    rf"(?P<kind>FAIL|ERROR): (?P<identity>[^\n]+)\n"
    rf"{re.escape(RULE)}\n"
    rf"(?P<body>.*?)"
    rf"(?=^{re.escape(SEPARATOR)}\n|^{re.escape(RULE)}\nRan )",
    re.MULTILINE | re.DOTALL,
)
ANY_RESULT_HEADING_RE = re.compile(r"^(FAIL|ERROR): .+$", re.MULTILINE)
RUN_RE = re.compile(
    rf"^{re.escape(RULE)}\n"
    r"Ran (?P<tests>[0-9]+) tests? in (?P<duration>[0-9]+(?:\.[0-9]+)?)s\n"
    r"\n(?P<summary>OK(?: \(skipped=[0-9]+\))?|FAILED \([^)]+\))$",
    re.MULTILINE,
)
ANY_RAN_RE = re.compile(r"^Ran [0-9]+ tests? in ", re.MULTILINE)
ANY_SUMMARY_RE = re.compile(
    r"^(?:OK(?: \(skipped=[0-9]+\))?|FAILED \([^)]+\))$", re.MULTILINE
)
COMMAND_STATUS_RE = re.compile(r"^command_status=(?P<status>-?[0-9]+)$", re.MULTILINE)
NAMED_SKIP_RE = re.compile(
    r"^(?P<identity>.+?) \.\.\. skipped (?P<reason>(?:'.*'|\".*\"))$"
)
UNNAMED_SKIP_RE = re.compile(r"^skipped (?P<reason>(?:'.*'|\".*\"))$")


class MalformedUnittestLog(ValueError):
    """Raised when captured unittest output is incomplete or contradictory."""


class MalformedEvidence(ValueError):
    """Raised when tracked normalized evidence violates its closed schema."""


class IdentityRegression(AssertionError):
    """Raised when a current run adds a failure or error identity."""


@dataclass(frozen=True)
class ResultRecord:
    kind: str
    identity: str
    block_sha256: str
    body_sha256: str


@dataclass(frozen=True)
class RawSkipRecord:
    raw_identity: Optional[str]
    reason: str
    line_sha256: str


@dataclass(frozen=True)
class ResolvedSkipRecord:
    raw_identity: Optional[str]
    resolved_identity: str
    reason: str
    line_sha256: str
    resolution_provenance: Mapping[str, str]


@dataclass(frozen=True)
class SkipResolution:
    line_sha256: str
    reason: str
    resolved_identity: str
    provenance: Mapping[str, str]


@dataclass(frozen=True)
class SkipResolverMap:
    format: str
    version: int
    resolutions: Mapping[str, SkipResolution]


@dataclass(frozen=True)
class RunEvidence:
    tests_run: int
    outcome: str
    failure_count: int
    error_count: int
    skipped_count: int
    command_status: Optional[int]
    failures: Tuple[ResultRecord, ...]
    errors: Tuple[ResultRecord, ...]
    skips: Tuple[RawSkipRecord, ...]


@dataclass(frozen=True)
class NormalizedEvidence:
    tests_run: int
    outcome: str
    failure_count: int
    error_count: int
    skipped_count: int
    command_status: int
    failures: Tuple[ResultRecord, ...]
    errors: Tuple[ResultRecord, ...]
    skips: Tuple[ResolvedSkipRecord, ...]
    format: str
    version: int
    source_log_size: int
    source_log_sha256: str


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _summary_counts(summary: str) -> tuple[str, dict[str, int]]:
    if summary == "OK":
        return "OK", {"failures": 0, "errors": 0, "skipped": 0}
    if summary.startswith("OK (skipped="):
        skipped = int(summary[len("OK (skipped="):-1])
        if skipped <= 0:
            raise MalformedUnittestLog("OK skip count must be positive")
        return "OK", {"failures": 0, "errors": 0, "skipped": skipped}
    if not summary.startswith("FAILED ("):
        raise MalformedUnittestLog("unrecognized unittest summary")

    counts = {"failures": 0, "errors": 0, "skipped": 0}
    seen = set()
    payload = summary[len("FAILED ("):-1]
    for field in payload.split(", "):
        if "=" not in field:
            raise MalformedUnittestLog("malformed FAILED summary field")
        key, value = field.split("=", 1)
        if key not in counts or key in seen or not value.isdigit():
            raise MalformedUnittestLog("unknown or duplicate FAILED summary field")
        parsed = int(value)
        if parsed <= 0:
            raise MalformedUnittestLog("FAILED summary counts must be positive")
        counts[key] = parsed
        seen.add(key)
    if not seen or counts["failures"] + counts["errors"] == 0:
        raise MalformedUnittestLog("FAILED summary has no failure or error")
    return "FAILED", counts


def _parse_skips(progress: str) -> tuple[RawSkipRecord, ...]:
    records = []
    for line in progress.splitlines():
        match = NAMED_SKIP_RE.fullmatch(line)
        identity: Optional[str]
        if match is not None:
            identity = match.group("identity")
        else:
            match = UNNAMED_SKIP_RE.fullmatch(line)
            if match is None:
                continue
            identity = None
        try:
            reason = ast.literal_eval(match.group("reason"))
        except (SyntaxError, ValueError) as exc:
            raise MalformedUnittestLog("invalid skip-reason representation") from exc
        if not isinstance(reason, str) or not reason:
            raise MalformedUnittestLog("skip reason must be a nonempty string")
        records.append(RawSkipRecord(identity, reason, _sha256(line)))
    return tuple(records)


def _validate_run_consistency(
    *,
    tests_run: int,
    outcome: str,
    failure_count: int,
    error_count: int,
    skipped_count: int,
    command_status: Optional[int],
    failures: tuple[ResultRecord, ...],
    errors: tuple[ResultRecord, ...],
    skips: Sequence[Any],
    error_type: type[ValueError],
) -> None:
    def reject(message: str) -> None:
        raise error_type(message)

    if tests_run <= 0:
        reject("vacuous unittest run")
    if failure_count != len(failures):
        reject("failure summary count contradicts structured blocks")
    if error_count != len(errors):
        reject("error summary count contradicts structured blocks")
    if skipped_count != len(skips):
        reject("skip summary count contradicts progress records")
    if failure_count + error_count + skipped_count > tests_run:
        reject("result counts exceed Ran total")
    if outcome == "OK":
        if failure_count or error_count:
            reject("OK summary contradicts failures or errors")
        if command_status not in (None, 0):
            reject("OK summary contradicts command_status")
    elif outcome == "FAILED":
        if failure_count + error_count == 0:
            reject("FAILED summary has no failure or error")
        if command_status not in (None, 1):
            reject("FAILED summary contradicts command_status")
    else:
        reject("outcome must be OK or FAILED")

    identities = [record.identity for record in failures + errors]
    if len(identities) != len(set(identities)):
        reject("duplicate result identity")


def parse_raw_unittest_log(output: str) -> RunEvidence:
    """Parse a complete delimiter-structured unittest capture fail closed."""

    if not isinstance(output, str) or not output:
        raise MalformedUnittestLog("empty unittest log")

    run_matches = list(RUN_RE.finditer(output))
    if (
        len(run_matches) != 1
        or len(ANY_RAN_RE.findall(output)) != 1
        or len(ANY_SUMMARY_RE.findall(output)) != 1
    ):
        raise MalformedUnittestLog("expected exactly one Ran trailer and summary")
    run_match = run_matches[0]

    blocks = list(RESULT_BLOCK_RE.finditer(output))
    structured_heading_starts = {match.start("kind") for match in blocks}
    all_heading_starts = {match.start() for match in ANY_RESULT_HEADING_RE.finditer(output)}
    if all_heading_starts != structured_heading_starts:
        raise MalformedUnittestLog("unstructured result heading")

    result_records = []
    for match in blocks:
        kind = match.group("kind")
        identity = match.group("identity")
        body = match.group("body")
        block = match.group(0)
        result_records.append(
            ResultRecord(kind, identity, _sha256(block), _sha256(body))
        )

    if blocks and blocks[-1].end() != run_match.start():
        between = output[blocks[-1].end():run_match.start()]
        if between:
            raise MalformedUnittestLog("trailing text between results and Ran trailer")
    if not blocks:
        prefix_end = run_match.start()
    else:
        prefix_end = blocks[0].start()
    skips = _parse_skips(output[:prefix_end])

    command_matches = list(COMMAND_STATUS_RE.finditer(output))
    if len(command_matches) > 1:
        raise MalformedUnittestLog("multiple command_status records")
    command_status = None
    if command_matches:
        command_match = command_matches[0]
        if command_match.start() <= run_match.end():
            raise MalformedUnittestLog("command_status must follow the summary")
        if output[run_match.end():command_match.start()].strip():
            raise MalformedUnittestLog(
                "non-whitespace between summary and command_status"
            )
        command_status = int(command_match.group("status"))
        if output[command_match.end():].strip():
            raise MalformedUnittestLog("command_status must be the final record")
    elif output[run_match.end():].strip():
        raise MalformedUnittestLog("summary must be the final record")

    outcome, counts = _summary_counts(run_match.group("summary"))
    failures = tuple(record for record in result_records if record.kind == "FAIL")
    errors = tuple(record for record in result_records if record.kind == "ERROR")
    tests_run = int(run_match.group("tests"))
    _validate_run_consistency(
        tests_run=tests_run,
        outcome=outcome,
        failure_count=counts["failures"],
        error_count=counts["errors"],
        skipped_count=counts["skipped"],
        command_status=command_status,
        failures=failures,
        errors=errors,
        skips=skips,
        error_type=MalformedUnittestLog,
    )
    return RunEvidence(
        tests_run,
        outcome,
        counts["failures"],
        counts["errors"],
        counts["skipped"],
        command_status,
        failures,
        errors,
        skips,
    )


def _require_exact_keys(
    value: Mapping[str, Any], keys: set[str], label: str
) -> None:
    if set(value) != keys:
        raise MalformedEvidence(f"{label} keys differ from closed schema")


def _require_int(value: Any, label: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise MalformedEvidence(f"{label} must be an integer >= {minimum}")
    return value


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise MalformedEvidence(f"{label} must be lowercase SHA-256")
    return value


def _require_nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise MalformedEvidence(f"{label} must be a nonempty string")
    return value


def _require_git_object(value: Any, label: str) -> str:
    if not isinstance(value, str) or GIT_OBJECT_RE.fullmatch(value) is None:
        raise MalformedEvidence(f"{label} must be a lowercase full Git object ID")
    return value


def _git_bytes(cwd: Path, arguments: Sequence[str], label: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), *arguments],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise MalformedEvidence(f"{label} is unavailable from Git history") from exc
    if result.returncode != 0:
        raise MalformedEvidence(f"{label} is unavailable from Git history")
    return result.stdout


def _historical_source_bytes(
    *,
    source_root: Path,
    relative_path: Path,
    source_revision: str,
    source_blob_sha1: str,
    label: str,
) -> bytes:
    top_level_raw = _git_bytes(
        source_root, ("rev-parse", "--show-toplevel"), f"{label} repository"
    )
    try:
        repository_root = Path(top_level_raw.decode("utf-8").strip()).resolve()
    except UnicodeDecodeError as exc:
        raise MalformedEvidence(f"{label} repository path is not UTF-8") from exc
    try:
        source_root_relative = source_root.relative_to(repository_root)
    except ValueError as exc:
        raise MalformedEvidence(f"{label} source root is outside its repository") from exc
    git_path = (source_root_relative / relative_path).as_posix()

    commit_raw = _git_bytes(
        repository_root,
        ("rev-parse", "--verify", f"{source_revision}^{{commit}}"),
        f"{label} source revision",
    )
    try:
        resolved_commit = commit_raw.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise MalformedEvidence(f"{label} source revision is not ASCII") from exc
    if resolved_commit != source_revision:
        raise MalformedEvidence(f"{label} source revision does not resolve exactly")

    blob_raw = _git_bytes(
        repository_root,
        ("rev-parse", f"{source_revision}:{git_path}"),
        f"{label} source path",
    )
    try:
        resolved_blob = blob_raw.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise MalformedEvidence(f"{label} source blob is not ASCII") from exc
    if resolved_blob != source_blob_sha1:
        raise MalformedEvidence(f"{label} source blob differs")
    object_type = _git_bytes(
        repository_root,
        ("cat-file", "-t", source_blob_sha1),
        f"{label} source blob",
    ).decode("ascii", errors="strict").strip()
    if object_type != "blob":
        raise MalformedEvidence(f"{label} source object is not a blob")
    return _git_bytes(
        repository_root,
        ("cat-file", "blob", source_blob_sha1),
        f"{label} source blob",
    )


def _unique_set_up_class(
    class_node: ast.ClassDef,
) -> ast.FunctionDef | None:
    methods = [
        node
        for node in class_node.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "setUpClass"
    ]
    if len(methods) != 1 or not isinstance(methods[0], ast.FunctionDef):
        return None
    method = methods[0]
    arguments = method.args
    if not (
        len(method.decorator_list) == 1
        and isinstance(method.decorator_list[0], ast.Name)
        and method.decorator_list[0].id == "classmethod"
        and not arguments.posonlyargs
        and len(arguments.args) == 1
        and arguments.args[0].arg == "cls"
        and arguments.vararg is None
        and not arguments.kwonlyargs
        and not arguments.kw_defaults
        and arguments.kwarg is None
        and not arguments.defaults
    ):
        return None
    return method


def _unique_top_level_class(module: ast.Module, name: str) -> ast.ClassDef | None:
    classes = [
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == name
    ]
    return classes[0] if len(classes) == 1 else None


def _scope_rebinds_unittest(nodes: Sequence[ast.AST]) -> bool:
    pending = list(nodes)
    while pending:
        node = pending.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == "unittest":
                return True
            continue
        if isinstance(node, ast.Lambda):
            continue
        if isinstance(node, ast.ExceptHandler) and node.name == "unittest":
            return True
        if isinstance(node, MATCH_BINDING_NODES) and node.name == "unittest":
            return True
        if (
            isinstance(node, ast.Name)
            and node.id == "unittest"
            and isinstance(node.ctx, (ast.Store, ast.Del))
        ):
            return True
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "unittest"
            and isinstance(node.ctx, (ast.Store, ast.Del))
        ):
            return True
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                bound_name = alias.asname or alias.name.split(".", 1)[0]
                if bound_name == "unittest":
                    return True
        pending.extend(ast.iter_child_nodes(node))
    return False


def _module_authenticates_unittest(
    module: ast.Module,
    selected_class: ast.ClassDef,
    set_up_class: ast.FunctionDef,
) -> bool:
    imports = [
        node
        for node in module.body
        if isinstance(node, ast.Import)
        and len(node.names) == 1
        and node.names[0].name == "unittest"
        and node.names[0].asname is None
    ]
    if len(imports) != 1:
        return False
    module_nodes = [node for node in module.body if node is not imports[0]]
    class_nodes = [node for node in selected_class.body if node is not set_up_class]
    return not (
        _scope_rebinds_unittest(module_nodes)
        or _scope_rebinds_unittest(class_nodes)
        or _scope_rebinds_unittest(set_up_class.body)
    )


def _call_has_exact_reason(call: ast.Call, reason: str) -> bool:
    return (
        len(call.args) == 1
        and not call.keywords
        and isinstance(call.args[0], ast.Constant)
        and isinstance(call.args[0].value, str)
        and call.args[0].value == reason
    )


def _is_skip_test_exception_call(call: ast.Call, reason: str) -> bool:
    if not _call_has_exact_reason(call, reason):
        return False
    function = call.func
    return (
        isinstance(function, ast.Attribute)
        and function.attr == "SkipTest"
        and isinstance(function.value, ast.Name)
        and function.value.id == "unittest"
    )


def _set_up_class_raises_skip_reason(
    set_up_class: ast.FunctionDef, reason: str
) -> bool:
    pending = list(set_up_class.body)
    matching_raises = 0
    while pending:
        node = pending.pop()
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)
        ):
            continue
        if (
            isinstance(node, ast.Raise)
            and isinstance(node.exc, ast.Call)
            and _is_skip_test_exception_call(node.exc, reason)
        ):
            matching_raises += 1
        pending.extend(ast.iter_child_nodes(node))
    return matching_raises == 1


def load_skip_resolver_map(
    data: Any, *, source_root: Path = OPENCFW_ROOT
) -> SkipResolverMap:
    """Load a vetted map that resolves anonymous unittest skip lines."""

    if not isinstance(data, Mapping):
        raise MalformedEvidence("skip resolver map must be an object")
    _require_exact_keys(data, {"format", "version", "resolutions"}, "resolver root")
    if (
        data["format"] != RESOLVER_FORMAT
        or data["version"] != RESOLVER_VERSION
    ):
        raise MalformedEvidence("unsupported skip resolver format/version")
    resolutions_data = data["resolutions"]
    if not isinstance(resolutions_data, list) or not resolutions_data:
        raise MalformedEvidence("resolver resolutions must be a nonempty array")

    source_root = source_root.resolve()
    resolutions: dict[str, SkipResolution] = {}
    resolved_identities = set()
    for index, item in enumerate(resolutions_data):
        label = f"resolutions[{index}]"
        if not isinstance(item, Mapping):
            raise MalformedEvidence(f"{label} must be an object")
        _require_exact_keys(
            item,
            {"line_sha256", "reason", "resolved_identity", "provenance"},
            label,
        )
        line_sha256 = _require_sha256(item["line_sha256"], f"{label}.line_sha256")
        reason = _require_nonempty_string(item["reason"], f"{label}.reason")
        resolved_identity = _require_nonempty_string(
            item["resolved_identity"], f"{label}.resolved_identity"
        )
        provenance = item["provenance"]
        if not isinstance(provenance, Mapping):
            raise MalformedEvidence(f"{label}.provenance must be an object")
        _require_exact_keys(
            provenance,
            {
                "method",
                "source_path",
                "source_class",
                "source_sha256",
                "source_revision",
                "source_blob_sha1",
            },
            f"{label}.provenance",
        )
        if provenance["method"] != "source_test_class_setUpClass":
            raise MalformedEvidence(f"{label}.provenance method is invalid")
        source_path_text = _require_nonempty_string(
            provenance["source_path"], f"{label}.provenance.source_path"
        )
        source_class = _require_nonempty_string(
            provenance["source_class"], f"{label}.provenance.source_class"
        )
        source_sha256 = _require_sha256(
            provenance["source_sha256"], f"{label}.provenance.source_sha256"
        )
        source_revision = _require_git_object(
            provenance["source_revision"],
            f"{label}.provenance.source_revision",
        )
        source_blob_sha1 = _require_git_object(
            provenance["source_blob_sha1"],
            f"{label}.provenance.source_blob_sha1",
        )
        relative_path = Path(source_path_text)
        if (
            relative_path.is_absolute()
            or relative_path.as_posix() != source_path_text
            or ".." in relative_path.parts
        ):
            raise MalformedEvidence(f"{label}.provenance.source_path is unsafe")
        source_bytes = _historical_source_bytes(
            source_root=source_root,
            relative_path=relative_path,
            source_revision=source_revision,
            source_blob_sha1=source_blob_sha1,
            label=f"{label}.provenance",
        )
        if hashlib.sha256(source_bytes).hexdigest() != source_sha256:
            raise MalformedEvidence(f"{label}.provenance source SHA-256 differs")
        try:
            source_tree = ast.parse(
                source_bytes.decode("utf-8"), filename=source_path_text
            )
        except (SyntaxError, UnicodeDecodeError) as exc:
            raise MalformedEvidence(
                f"{label}.provenance source is not valid Python"
            ) from exc
        selected_class = _unique_top_level_class(source_tree, source_class)
        set_up_class = (
            _unique_set_up_class(selected_class)
            if selected_class is not None
            else None
        )
        if set_up_class is None:
            raise MalformedEvidence(
                f"{label}.provenance class setUpClass is not uniquely present"
            )
        if not _module_authenticates_unittest(
            source_tree, selected_class, set_up_class
        ):
            raise MalformedEvidence(
                f"{label}.provenance unittest binding is not uniquely authenticated"
            )
        expected_identity = f"setUpClass ({relative_path.stem}.{source_class})"
        if resolved_identity != expected_identity:
            raise MalformedEvidence(f"{label}.resolved_identity contradicts source")
        if not _set_up_class_raises_skip_reason(set_up_class, reason):
            raise MalformedEvidence(
                f"{label}.reason is not raised by the selected class setUpClass"
            )
        if line_sha256 in resolutions:
            raise MalformedEvidence("duplicate resolver line SHA-256")
        if resolved_identity in resolved_identities:
            raise MalformedEvidence("duplicate resolver identity")
        provenance_record = {
            "method": provenance["method"],
            "source_path": source_path_text,
            "source_class": source_class,
            "source_sha256": source_sha256,
            "source_revision": source_revision,
            "source_blob_sha1": source_blob_sha1,
        }
        resolutions[line_sha256] = SkipResolution(
            line_sha256,
            reason,
            resolved_identity,
            provenance_record,
        )
        resolved_identities.add(resolved_identity)
    return SkipResolverMap(
        data["format"], data["version"], resolutions
    )


def _resolved_skips(
    skips: Sequence[RawSkipRecord], resolver_map: SkipResolverMap
) -> tuple[ResolvedSkipRecord, ...]:
    records = []
    identities = set()
    for index, record in enumerate(skips):
        if record.raw_identity is not None:
            resolved_identity = record.raw_identity
            provenance = {"method": "raw_unittest_output"}
        else:
            resolution = resolver_map.resolutions.get(record.line_sha256)
            if resolution is None:
                raise MalformedEvidence(
                    f"skips[{index}] has no vetted anonymous resolution"
                )
            if resolution.reason != record.reason:
                raise MalformedEvidence(
                    f"skips[{index}] reason contradicts vetted resolution"
                )
            resolved_identity = resolution.resolved_identity
            provenance = dict(resolution.provenance)
        if resolved_identity in identities:
            raise MalformedEvidence("resolved skip identities must be unique")
        identities.add(resolved_identity)
        records.append(ResolvedSkipRecord(
            record.raw_identity,
            resolved_identity,
            record.reason,
            record.line_sha256,
            provenance,
        ))
    return tuple(records)


def load_normalized_evidence(
    data: Any, resolver_map: SkipResolverMap
) -> NormalizedEvidence:
    """Validate and load the durable normalized evidence schema."""

    if not isinstance(data, Mapping):
        raise MalformedEvidence("normalized evidence must be an object")
    _require_exact_keys(
        data, {"format", "version", "source_log", "run", "results", "skips"}, "root"
    )
    if data["format"] != FORMAT or data["version"] != VERSION:
        raise MalformedEvidence("unsupported normalized evidence format/version")

    source = data["source_log"]
    run = data["run"]
    results = data["results"]
    skips_data = data["skips"]
    if not isinstance(source, Mapping) or not isinstance(run, Mapping):
        raise MalformedEvidence("source_log and run must be objects")
    if not isinstance(results, list) or not isinstance(skips_data, list):
        raise MalformedEvidence("results and skips must be arrays")
    _require_exact_keys(source, {"size", "sha256", "command_status"}, "source_log")
    _require_exact_keys(
        run, {"tests", "outcome", "failures", "errors", "skips"}, "run"
    )

    result_records = []
    for index, item in enumerate(results):
        if not isinstance(item, Mapping):
            raise MalformedEvidence(f"results[{index}] must be an object")
        _require_exact_keys(
            item, {"kind", "identity", "block_sha256", "body_sha256"},
            f"results[{index}]",
        )
        if item["kind"] not in ("FAIL", "ERROR"):
            raise MalformedEvidence(f"results[{index}].kind is invalid")
        if not isinstance(item["identity"], str) or not item["identity"]:
            raise MalformedEvidence(f"results[{index}].identity is invalid")
        result_records.append(ResultRecord(
            item["kind"],
            item["identity"],
            _require_sha256(item["block_sha256"], f"results[{index}].block_sha256"),
            _require_sha256(item["body_sha256"], f"results[{index}].body_sha256"),
        ))

    skip_records = []
    for index, item in enumerate(skips_data):
        if not isinstance(item, Mapping):
            raise MalformedEvidence(f"skips[{index}] must be an object")
        _require_exact_keys(
            item,
            {
                "raw_identity",
                "resolved_identity",
                "reason",
                "line_sha256",
                "resolution_provenance",
            },
            f"skips[{index}]",
        )
        raw_identity = item["raw_identity"]
        if raw_identity is not None and (
            not isinstance(raw_identity, str) or not raw_identity
        ):
            raise MalformedEvidence(f"skips[{index}].raw_identity is invalid")
        resolved_identity = _require_nonempty_string(
            item["resolved_identity"], f"skips[{index}].resolved_identity"
        )
        reason = _require_nonempty_string(item["reason"], f"skips[{index}].reason")
        line_sha256 = _require_sha256(
            item["line_sha256"], f"skips[{index}].line_sha256"
        )
        provenance = item["resolution_provenance"]
        if not isinstance(provenance, Mapping):
            raise MalformedEvidence(
                f"skips[{index}].resolution_provenance must be an object"
            )
        raw_record = RawSkipRecord(raw_identity, reason, line_sha256)
        expected = _resolved_skips((raw_record,), resolver_map)[0]
        if (
            resolved_identity != expected.resolved_identity
            or dict(provenance) != expected.resolution_provenance
        ):
            raise MalformedEvidence(
                f"skips[{index}] resolution or provenance is not vetted"
            )
        skip_records.append(ResolvedSkipRecord(
            raw_identity,
            resolved_identity,
            reason,
            line_sha256,
            dict(provenance),
        ))

    resolved_identities = [record.resolved_identity for record in skip_records]
    if len(resolved_identities) != len(set(resolved_identities)):
        raise MalformedEvidence("resolved skip identities must be unique")

    failures = tuple(record for record in result_records if record.kind == "FAIL")
    errors = tuple(record for record in result_records if record.kind == "ERROR")
    tests_run = _require_int(run["tests"], "run.tests", minimum=1)
    failure_count = _require_int(run["failures"], "run.failures")
    error_count = _require_int(run["errors"], "run.errors")
    skipped_count = _require_int(run["skips"], "run.skips")
    command_status = _require_int(source["command_status"], "source_log.command_status")
    if not isinstance(run["outcome"], str):
        raise MalformedEvidence("run.outcome must be a string")
    _validate_run_consistency(
        tests_run=tests_run,
        outcome=run["outcome"],
        failure_count=failure_count,
        error_count=error_count,
        skipped_count=skipped_count,
        command_status=command_status,
        failures=failures,
        errors=errors,
        skips=tuple(skip_records),
        error_type=MalformedEvidence,
    )
    return NormalizedEvidence(
        tests_run,
        run["outcome"],
        failure_count,
        error_count,
        skipped_count,
        command_status,
        failures,
        errors,
        tuple(skip_records),
        data["format"],
        data["version"],
        _require_int(source["size"], "source_log.size", minimum=1),
        _require_sha256(source["sha256"], "source_log.sha256"),
    )


def normalized_evidence_dict(
    raw: RunEvidence, source_bytes: bytes, resolver_map: SkipResolverMap
) -> dict[str, Any]:
    """Return the deterministic durable representation for a parsed raw log."""

    if raw.command_status is None:
        raise MalformedUnittestLog("normalized evidence requires command_status")
    resolved_skips = _resolved_skips(raw.skips, resolver_map)
    return {
        "format": FORMAT,
        "version": VERSION,
        "source_log": {
            "size": len(source_bytes),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "command_status": raw.command_status,
        },
        "run": {
            "tests": raw.tests_run,
            "outcome": raw.outcome,
            "failures": raw.failure_count,
            "errors": raw.error_count,
            "skips": raw.skipped_count,
        },
        "results": [
            {
                "kind": record.kind,
                "identity": record.identity,
                "block_sha256": record.block_sha256,
                "body_sha256": record.body_sha256,
            }
            for record in raw.failures + raw.errors
        ],
        "skips": [
            {
                "raw_identity": record.raw_identity,
                "resolved_identity": record.resolved_identity,
                "reason": record.reason,
                "line_sha256": record.line_sha256,
                "resolution_provenance": dict(record.resolution_provenance),
            }
            for record in resolved_skips
        ],
    }


def require_no_new_failures_or_errors(
    baseline: NormalizedEvidence, current: RunEvidence
) -> None:
    """Reject result identities absent from the durable baseline."""

    baseline_failures = {record.identity for record in baseline.failures}
    baseline_errors = {record.identity for record in baseline.errors}
    current_failures = {record.identity for record in current.failures}
    current_errors = {record.identity for record in current.errors}
    new_failures = sorted(current_failures - baseline_failures)
    new_errors = sorted(current_errors - baseline_errors)
    if new_failures or new_errors:
        failure_text = ", ".join(new_failures) or "none"
        error_text = ", ".join(new_errors) or "none"
        raise IdentityRegression(
            f"new failures: {failure_text}; new errors: {error_text}"
        )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-resolvers",
        required=True,
        type=Path,
        help="vetted anonymous-skip resolver map",
    )
    parser.add_argument("baseline", type=Path)
    parser.add_argument("current", type=Path)
    args = parser.parse_args(argv)
    try:
        resolver_map = load_skip_resolver_map(
            json.loads(args.skip_resolvers.read_text(encoding="utf-8"))
        )
        baseline = load_normalized_evidence(
            json.loads(args.baseline.read_text(encoding="utf-8")),
            resolver_map,
        )
        current = parse_raw_unittest_log(args.current.read_text(encoding="utf-8"))
        require_no_new_failures_or_errors(baseline, current)
    except (MalformedEvidence, MalformedUnittestLog, IdentityRegression) as exc:
        parser.exit(1, f"{exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
