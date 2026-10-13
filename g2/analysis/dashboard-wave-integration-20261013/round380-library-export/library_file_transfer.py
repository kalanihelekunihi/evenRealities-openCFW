#!/usr/bin/env python3
# ruff: noqa: TID251
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

LIBRARY_FILE_ID_XATTR_NAME = "user.library-file-id"


class LibraryFileTransferError(Exception):
    pass


def require_object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise LibraryFileTransferError(f"{label} must be a JSON object")
    result: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise LibraryFileTransferError(f"{label} keys must be strings")
        result[key] = item
    return result


def require_string(value: object, label: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        qualification = "" if allow_empty else " non-empty"
        raise LibraryFileTransferError(f"{label} must be a{qualification} string")
    return value


@dataclass(frozen=True)
class ExtendedAttribute:
    name: str
    value: str

    @classmethod
    def parse(cls, value: object, index: int) -> "ExtendedAttribute":
        payload = require_object(value, f"xattrs[{index}]")
        return cls(
            name=require_string(payload.get("name"), f"xattrs[{index}].name"),
            value=require_string(
                payload.get("value"),
                f"xattrs[{index}].value",
                allow_empty=True,
            ),
        )

    def apply(self, path: Path) -> None:
        encoded_value = self.value.encode()
        if sys.platform == "darwin":
            actual_value = self._apply_darwin(path, encoded_value)
        else:
            os.setxattr(path, self.name, encoded_value)
            actual_value = os.getxattr(path, self.name)
        if actual_value != encoded_value:
            raise LibraryFileTransferError(f"failed to verify extended attribute {self.name!r}")

    def _apply_darwin(self, path: Path, encoded_value: bytes) -> bytes:
        try:
            subprocess.run(
                ["/usr/bin/xattr", "-wx", self.name, encoded_value.hex(), path],
                check=True,
                capture_output=True,
            )
            result = subprocess.run(
                ["/usr/bin/xattr", "-px", self.name, path],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            raise LibraryFileTransferError(
                f"failed to apply extended attribute {self.name!r}"
            ) from exc
        return bytes.fromhex(result.stdout)


def parse_xattrs(value: object) -> tuple[ExtendedAttribute, ...]:
    if not isinstance(value, list):
        raise LibraryFileTransferError("xattrs must be a JSON array")
    return tuple(ExtendedAttribute.parse(item, index) for index, item in enumerate(value))


def include_library_file_id_xattr(
    xattrs: tuple[ExtendedAttribute, ...],
    library_file_id: str | None,
) -> tuple[ExtendedAttribute, ...]:
    if library_file_id is None:
        return xattrs
    return (
        *(xattr for xattr in xattrs if xattr.name != LIBRARY_FILE_ID_XATTR_NAME),
        ExtendedAttribute(name=LIBRARY_FILE_ID_XATTR_NAME, value=library_file_id),
    )


def _is_trusted_estuary_download(download_url: str) -> bool:
    download = urllib.parse.urlsplit(download_url)
    hosted_apps = urllib.parse.urlsplit(
        os.environ.get("CODEX_APPS_MCP_URL", "https://chatgpt.com/backend-api/wham/apps")
    )
    try:
        same_origin = (download.hostname, 443 if download.port is None else download.port) == (
            hosted_apps.hostname,
            443 if hosted_apps.port is None else hosted_apps.port,
        )
    except ValueError:
        return False
    prefix = "/backend-api/estuary/public_content/enc/"
    return (
        download.scheme == hosted_apps.scheme == "https"
        and same_origin
        and download.username is None
        and download.password is None
        and download.path.startswith(prefix)
        and re.fullmatch(r"[A-Za-z0-9_-]+={0,2}", download.path[len(prefix) :]) is not None
        and not download.query
        and not download.fragment
    )


def _estuary_auth_headers(download_url: str) -> dict[str, str]:
    if not _is_trusted_estuary_download(download_url):
        return {}
    authorization = os.environ.get("CODEX_APPS_AUTHORIZATION", "").strip()
    account_id = os.environ.get("CODEX_APPS_CHATGPT_ACCOUNT_ID", "").strip()
    if not authorization:
        token = os.environ.get("CODEX_CONNECTORS_TOKEN", "").strip()
        if not token:
            auth_path = Path(
                os.environ.get("CODEX_AUTH_PATH")
                or Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
            ).expanduser()
            try:
                payload = require_object(json.loads(auth_path.read_text()), "Codex auth")
                tokens = require_object(payload.get("tokens"), "Codex auth tokens")
                token = require_string(tokens.get("access_token"), "Codex access token")
                if token == "access_token":
                    return {}
                account_id = account_id or str(tokens.get("account_id") or "")
            except (OSError, json.JSONDecodeError, LibraryFileTransferError):
                return {}
        authorization = f"Bearer {token}"
    headers = {"Authorization": authorization}
    if account_id:
        headers["ChatGPT-Account-ID"] = account_id
    return headers


class _NoAuthenticatedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args: object) -> None:
        return None


@dataclass(frozen=True)
class LibraryFileTransfer:
    download_url: str
    headers: dict[str, str]
    library_file_id: str | None
    xattrs: tuple[ExtendedAttribute, ...]

    @classmethod
    def parse(cls, value: object) -> "LibraryFileTransfer":
        payload = require_object(value, "transfer")
        raw_headers = require_object(payload.get("headers", {}), "transfer.headers")
        headers = {
            name: require_string(header_value, f"transfer.headers[{name!r}]")
            for name, header_value in raw_headers.items()
        }
        return cls(
            download_url=require_string(payload.get("download_url"), "transfer.download_url"),
            headers=headers,
            library_file_id=(
                require_string(payload["library_file_id"], "transfer.library_file_id")
                if payload.get("library_file_id") is not None
                else None
            ),
            xattrs=parse_xattrs([] if payload.get("xattrs") is None else payload["xattrs"]),
        )

    def write_to(self, destination: Path) -> None:
        headers = {} if _is_trusted_estuary_download(self.download_url) else self.headers
        request = urllib.request.Request(self.download_url, headers=headers, method="GET")
        auth_headers = _estuary_auth_headers(self.download_url)
        for name, value in auth_headers.items():
            request.add_unredirected_header(name, value)
        urlopen = (
            urllib.request.build_opener(_NoAuthenticatedRedirect()).open
            if auth_headers
            else urllib.request.urlopen
        )
        try:
            with (
                urlopen(request, timeout=300) as response,
                destination.open("wb") as output,
            ):
                shutil.copyfileobj(response, output)
        except urllib.error.HTTPError as exc:
            raise LibraryFileTransferError(f"download failed with HTTP status {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise LibraryFileTransferError("download failed") from exc


class LibraryFileMaterializer:
    def materialize(self, transfer: LibraryFileTransfer, destination: Path) -> None:
        self._require_absolute_path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        file_descriptor, temporary_name = tempfile.mkstemp(
            dir=destination.parent,
            prefix=f".{destination.name}.",
        )
        os.close(file_descriptor)
        temporary_path = Path(temporary_name)
        try:
            transfer.write_to(temporary_path)
            self.apply_xattrs(
                include_library_file_id_xattr(
                    transfer.xattrs,
                    transfer.library_file_id,
                ),
                temporary_path,
            )
            os.replace(temporary_path, destination)
        finally:
            temporary_path.unlink(missing_ok=True)

    def apply_xattrs(
        self,
        xattrs: tuple[ExtendedAttribute, ...],
        path: Path,
    ) -> None:
        self._require_absolute_path(path)
        if not path.is_file():
            raise LibraryFileTransferError(f"file does not exist: {path}")
        for xattr in xattrs:
            xattr.apply(path)

    @staticmethod
    def _require_absolute_path(path: Path) -> None:
        if not path.is_absolute():
            raise LibraryFileTransferError("file path must be absolute")


def load_stdin_json() -> object:
    if sys.stdin.isatty():
        raise LibraryFileTransferError("stdin must be closed after one complete JSON request")
    try:
        value: object = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        raise LibraryFileTransferError("stdin must contain valid JSON") from exc
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Materialize a ChatGPT Library transfer and preserve its extended attributes.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    materialize_parser = subparsers.add_parser("materialize")
    materialize_parser.add_argument("destination", type=Path)
    apply_parser = subparsers.add_parser("apply-xattrs")
    apply_parser.add_argument("path", type=Path)
    apply_parser.add_argument("library_file_id")
    return parser


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    materializer = LibraryFileMaterializer()
    try:
        if args.command == "materialize":
            materializer.materialize(
                LibraryFileTransfer.parse(load_stdin_json()),
                args.destination,
            )
            print(args.destination)
        else:
            materializer.apply_xattrs(
                include_library_file_id_xattr(
                    parse_xattrs(load_stdin_json()),
                    require_string(args.library_file_id, "library_file_id"),
                ),
                args.path,
            )
            print(args.path)
    except (LibraryFileTransferError, OSError) as exc:
        print(f"library file transfer failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

