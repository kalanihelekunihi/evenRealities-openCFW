# Locally downloaded vendor tools

`manifest.json` records inspected filenames, versions and SHA-256 identities.
`setup.py` preserves Downloads originals and creates independent copies under
`third-party/local-vendor/`, which is explicitly ignored by Git. No keys belong
in either directory. Copies are not installed or activated tools.

| Download | What it supplies | Current use / limitation |
|---|---|---|
| `AmbiqSuite_R3.2.0/` | `release_sdk_3_2_0-dd5f40c14b`, source/docs for Apollo3 and Apollo3P | Locally staged SDK; not Apollo510 HAL. Keep the existing pinned Apollo510 HAL 5.1.0 candidate for G2. |
| `csky工具链.zip` | C-SKY ABIv2 v3.10.15, GCC 6.3.0; includes CK804 support | Extracted local toolchain; gcc version executes in Linux amd64 container. Not a GX8002 device SDK. |
| `T9305_EMB_SDK_installer.sh.zip` | EM9305 EM BLEU SDK v4.6, ARC EM7D source/libraries/tools | Prior agreement acceptance confirmed; copied and safely extracted locally via `install-em.py`; authenticated archive inventory passed (7,439 unique file paths). Existing stock library matches are for v4.2, not this download. |
| `ewarm-10.10.2.26960.exe` | IAR EWARM 10.10.2 Windows installer | Locally retained; never run on macOS. Not the stock-candidate IAR 9.60.2 version. |
| `MDK543a.exe` | Keil MDK 5.43a Windows installer | Locally retained; never run on macOS. |
| `iar-lmsc-tools_1.14_amd64.deb` | IAR Linux license-manager tooling | Installed with IAR Base in the amd64 container; iarlogin1.4.0 runs, activation not attempted. |
| `cxarm-10.10.2.27058.deb` | IAR Build Tools for ARM, Ubuntu amd64 | Await completed download and local checksum registration; not part of the locked manifest yet. |

## Local setup

Run from the repository root. Default actions are dry runs; `--apply` performs
only authenticated local copies or the explicitly supported data extraction.

```sh
python3 third-party/downloaded/setup.py stage
python3 third-party/downloaded/setup.py stage --apply
python3 third-party/downloaded/setup.py check
python3 third-party/downloaded/setup.py extract --id csky --apply
python3 third-party/downloaded/install-csky.py --apply
python3 third-party/downloaded/install-em.py --apply
git check-ignore -v third-party/local-vendor/artifacts/MDK543a.exe
```

Use `--downloads /absolute/path` for another download directory, or repeat
`--id` to select packages. Existing verified copies are left intact; mismatches
fail without overwriting. Directory identity includes every regular file.
The script rejects symlinks and unsafe ZIP paths/types and limits expansion.
It does not execute shell installers, unpack restricted EM source, install
Windows software, accept agreements, fetch packages, or activate licenses.

`install-csky.py` authenticates both nested archive levels, uses safe tar
extraction into ignored `local-vendor/toolchains/csky-linux-x86_64`, and checks
GCC version plus a freestanding CK804 compilation in the existing Linux amd64
Docker engine. The toolchain mount is read-only; only its owned scratch check
directory is writable. No repo-wide mount, networking or credentials are used.

## Linux container path

This Mac is Apple Silicon. Existing Colima uses aarch64 Linux; IAR's current
Linux package is amd64 and needs emulation, not a native ARM execution claim.
The preflight script tests the existing Docker engine with an isolated official
Ubuntu 24.04 amd64 container, with no host mounts or credentials:

```sh
sh third-party/downloaded/linux-preflight.sh
sh third-party/downloaded/linux-preflight.sh --apply
```

Successful `uname` establishes amd64 user-space execution only. It does not
establish compiler dependencies, licensing, performance, or stock byte equality.
Once both Linux DEBs are downloaded, inspect their control metadata, scripts and
license text as data, register checksums, then install into an isolated image
only after any explicit vendor agreement acceptance is resolved. Never place
the key from `~/Repo/apis` in a Dockerfile, build argument, environment log,
repository file or image layer. Activation requires secure user entry, and
Windows-key eligibility for the Linux subscription is not established.

`python3 third-party/downloaded/install-linux.py` previews this installation.
After review, checksum registration and explicit user acceptance, run it with
`--apply --license-accepted`. It refuses missing/unregistered packages, builds
only from a fixed package whitelist, and never activates a license. Its apt
dependency resolution needs network access; the resulting image must still be
tested before claiming usable IAR tooling.

## Licenses and evidence

Ambiq's top-level BSD-3-Clause notice also points to component-specific terms
in `docs/licenses`. C-SKY's included compiler/runtime components have their own
licenses. Local staging grants no blanket redistribution rights.
The EM agreement says access/copy/use constitutes acceptance and includes
confidentiality, transfer and binary reverse-engineering restrictions. User
confirmed prior acceptance at 15:26 UTC; the manifest records that decision.
`install-em.py` authenticates and safely unpacks data without executing its
shell installer, activation tools or SDK binaries. Accepted terms remain in force.

Detailed local inspection evidence:

- `third-party/downloaded/AGREEMENTS.md`: exact agreement paths, acceptance evidence and material restrictions.

- `g2/analysis/bootloader-completion-2026-10-06/upstream-worker/downloaded-sdks/SDK-INSPECTION.md`
- `g2/analysis/bootloader-completion-2026-10-06/review-worker/downloaded-tools/installer-review.md`

The Windows installers contain certificate-table data, but that inspection did
not establish Authenticode validity. Recorded hashes identify the supplied
files, not vendor-authenticated signatures. No firmware flashing is involved.

Official host-platform references:
[IAR requirements](https://netstorage.iar.com/FileStore/STANDARD/001/004/477/ew/doc/infocenter/installation.ENU.html),
[IAR Linux packages](https://updates.iar.com/?product=CXARM),
[Keil MDK options](https://www.keil.arm.com/keil-mdk/).

## IAR Linux Base: verified official alternate

The official release archive is now retained at
`third-party/local-vendor/artifacts/cxarm-10.10.2-linux-x86_64-base.tar.bz2`.
The user's Downloads original is preserved. Size: 382,973,847 bytes;
SHA-256: `b4fe2e43ec6e40e574f15a624e3c41f855cddf1e816ce852b1811bf10353cdb0`.
The release supplies a matching `.sha256` sidecar. Its README identifies
Build Tools for Arm **10.10.2.27058**, supporting Ubuntu24.04/26.04 amd64.
The archive and Ubuntu `.deb` are different packaging; equal version text
does not prove equal package contents or stock-firmware build output.

Reinstall locally (default invocation is a dry run):

```sh
python3 third-party/downloaded/install-iar-archive.py
python3 third-party/downloaded/install-iar-archive.py --apply
```

The script authenticates the archive, bounds and safely extracts it to
`third-party/local-vendor/toolchains/iar-linux-x86_64/cxarm-10.10.2`, then builds
`opencfw/iar-base:10.10.2-local` from a whitelisted ignored context at
`third-party/local-vendor/iar-base-container-build`. Its bundled EULA PDF hash
matches the already reviewed/accepted LMSC EULA exactly. The separate
`IARSourceLicense.txt` permits vendor runtime/startup source only with IAR
products and requires retaining notices. Vendor source stays local/ignored;
it is not silently mixed into the independently reconstructed Clang modules.

Official provenance:
[release](https://github.com/iarsystems/arm/releases/tag/10.10.2),
[Base archive](https://github.com/iarsystems/arm/releases/download/10.10.2/cxarm-10.10.2-linux-x86_64-base.tar.bz2),
[installation guide](https://github.com/iarsystems/arm/blob/main/INSTALLATION.md).

## Container layout decision

Use the existing **single Colima engine**, a **shared pinned Ubuntu24.04
linux/amd64 base**, and **separate tool environments**. No second VM is needed.
IAR gets its own image because its proprietary tool tree and activation
requirements should not become dependencies of unrelated C-SKY/analysis jobs.
C-SKY already runs and compiles the CK804 probe in the shared Ubuntu runtime
with a read-only toolchain mount; no extra dedicated C-SKY image is needed
until actual additional dependencies justify one. Ambiq and EM remain ignored
source SDK trees mounted only by jobs that need them. Ambiq3.2.0 supports
Apollo3/3P, not the bootloader's Apollo510; EM requires a compatible MetaWare
ARC toolchain, which has not been installed. Windows IAR/Keil installers are
retained originals, not usable Linux installations.

The shared base is `ubuntu:24.04` pinned to
`sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55`.
IAR uses `/opt/iar/cxarm-10.10.2/arm/bin` and `common/bin` on PATH. Example
version check, with no credentials or network:

```sh
docker run --rm --platform linux/amd64 --network none --cap-drop ALL \
  --security-opt no-new-privileges opencfw/iar-base:10.10.2-local iccarm --version
```

For builds, mount only the required source directory read-only and a specific
scratch/output directory writable at `/work`. Do not mount the whole home,
`~/Repo/apis`, browser profiles, Docker socket or device nodes. No privileged
container or hardware access is needed for these offline tasks.

Installation/version checks are separate from activation and licensed
compilation. The official archive guide requires an IAR subscription activation
token. Provision any required credential yourself through a secure runtime
mechanism after checking license entitlement; never put it in Dockerfiles,
build arguments, source files, manifests or image layers. These setup scripts
do not access a key, set a token, activate a license or flash anything.

Verified status: IAR compiler version execution succeeded (`V10.10.2.628/LNX for ARM`). An offline owned Cortex-M55 probe returned `LMSC2143`, requiring a bearer token or iarlogin, and produced no object. This is an activation/authentication boundary, not a source/compiler-install failure. The Base installer also authenticates and installs the supplied LMSC Tools1.14 package so iarlogin is available for a secure user login. No credential was accessed or activation attempted. Ubuntu package dependencies come from normal current repositories; the pinned base/archive and final image identity are recorded, but apt repositories are not a historical snapshot.

Final installed image: `sha256:af35f7f439b4af1827cdbfffe1f0895540b2aaf8c6a19ff5059e4250047e37d0` (linux/amd64). Compiler, linker and assembler version commands pass; iarbuild9.5.4.2231 starts with no missing loader dependencies, C-SPY9.5.4.2231 help passes and C-STAT2.11.0.945 version passes. The owned probe remains blocked by authentication. Evidence: `g2/analysis/bootloader-completion-2026-10-06/iar-container-verification.json`.

The legacy Docker builder failed exporting a content digest. Buildx0.37.2 resolved that error. On this Mac the installer uses a dedicated ignored `docker-build-config/config.json` containing only the plugin directory and explicitly connects to the existing Colima Unix socket. It does not read or modify your normal credential-bearing Docker configuration, prune images or restart the engine. Fresh setup requires Docker/Colima and Buildx (`brew install docker-buildx` on this Mac).

For secure user authentication, run the supported login command yourself in your IAR runtime environment: `iarlogin login --use-device-code --no-open`. Follow the displayed vendor verification instructions in your own browser. Use a private persistent HOME volume for that runtime so authentication state does not enter build images; do not run a login/token command during image build. No agent login, `show-token`, key lookup or token entry has occurred. Licensed compilation can be rechecked after that user step.

## Exact secure local authentication flow

Run this **yourself in a local interactive terminal**:

```sh
sh third-party/downloaded/login-iar.sh
```

It creates or reuses `opencfw-iar-session` from the verified IAR image, with a
stable hostname and private named HOME volume `opencfw-iar-user-home`. The
actual supported authentication command is:

```sh
docker exec -it opencfw-iar-session iarlogin login --use-device-code --no-open
```

Follow the verification URL displayed by the tool in your own browser and
enter its device code there. No credential/token is passed in command-line
arguments or requested in chat. `iarlogin login-status` checks the result;
no `show-token` command is used. The installed v1.4.0 help confirms the
hyphenated option spelling above; older online examples use underscores.

The persistent runtime container and its private HOME volume retain local
client state outside the build image. Retaining the same runtime container
also preserves any client state outside HOME. Never commit this authenticated
container as an image or copy its state into a build context. End-to-end
login and post-restart authentication persistence remain user-verification
steps because the agent has not authenticated or inspected credential files.

Named-user login needs an IAR account assigned suitable IAR Build Tools for
Arm subscription entitlement; a vendor-issued capacity token is the other
supported route. A preexisting Windows/perpetual license is not proof of that
cloud entitlement. If your account has none, resolve it with your IAR license
administrator/support. The installed compiler's `LMSC2143` identifies only
missing local authentication; it does not establish missing entitlement.

Ordinary online licensed compilation needs connectivity to IAR Cloud.
`--network none` was appropriate for the unactivated diagnostic probe, not
for assuming an online authenticated build will work. Optional offline
checkout is a separate user decision: it reserves account/capacity for up to
seven days and affects online availability elsewhere. This setup does not
perform checkout/checkin, token creation, login or license activation.

Official references:
[account/device authentication](https://docs.iar.com/lmsc/en/installation/installing-on-windows.html),
[iarlogin commands](https://docs.iar.com/lmsc/en/reference-information/iarlogin.html),
[offline licensing](https://docs.iar.com/lmsc/en/using-the-iar-cloud-based-licensing-system-offline.html),
[archive subscription requirements](https://github.com/iarsystems/arm/blob/main/INSTALLATION.md).
