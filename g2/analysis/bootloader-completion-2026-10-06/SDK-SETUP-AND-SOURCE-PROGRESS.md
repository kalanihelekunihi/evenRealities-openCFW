# Downloaded dependencies and continuing bootloader implementation

## Delivered local setup

Repository guide: `third-party/downloaded/README.md`. Checksum manifest:
`third-party/downloaded/manifest.json`. Reproducible local-copy/data-extraction
script: `setup.py`; container preflight: `linux-preflight.sh`; gated isolated
IAR installation script: `install-linux.py`, all in that same directory.

Verified independent copies of AmbiqSuite R3.2.0, C-SKY toolchain ZIP, IAR
Windows 10.10.2.26960, Keil MDK543a and Linux LMSC Tools 1.14 are under
`third-party/local-vendor/`. The C-SKY outer ZIP was extracted as data only.
The originals remain in Downloads. All copies passed manifest checksums.
`.gitignore:150` excludes the local vendor tree; `git check-ignore -v` confirms
that rule for SDK source and installer paths. No local vendor files are staged.
The existing index hash was preserved throughout this setup.

These are retained SDK materials and installer packages, not claims that the
compiler tools have been installed or executed. EM v4.6 remains in Downloads:
its access/copy/use agreement requires an explicit acceptance decision before
further use. IAR Linux compiler `cxarm-10.10.2.27058.deb` had not appeared as a
completed file at this check; only `iar-lmsc-tools_1.14_amd64.deb` was present.
No key was read, copied, transmitted or activated.

The actual existing Colima profile is running aarch64 Linux, 4 CPUs, 8 GiB RAM,
40 GiB disk, Docker 29.5.2. An isolated `linux/amd64` Ubuntu 24.04 container
executed `uname -m` and returned `x86_64`. Pulled image digest:
`sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55`.
This proves basic emulation, not IAR execution, entitlement or performance.
Sandbox-only socket checks initially failed; approved read-only runtime checks
established the running engine. No VM settings or OS security settings changed.

LMSC DEB control metadata confirms amd64, version 1.14. Inspected postinst only
creates `/usr/local/bin/iarlogin` symlink; postrm removes it. Agreement PDF was
extracted as data into ignored storage; no package installation occurred. IAR
agreement acceptance and secure activation remain separate required steps.

## Concrete bootloader progress

New downloaded Ambiq sources target Apollo3/3P, so they cannot substitute for
Apollo510. Existing pinned Apollo510 public HAL remains the defensible candidate.
Using that source, `g2/components/bootloader/mspi/verify.py` now compares the
stock function at `0x426506` with the real compiled public HAL adapter.
**PASS 37 cases / 48 distinct original instruction bytes**, covering null/invalid
handles, masked valid signatures, modules 0..2 and interrupt masks. No returning
provider stubs occur in this leaf. Stock clears INTCLR at module base +0x208,
then reads INTSTAT +0x204; the original decompiler omitted that read. Register
pages are synthetic, so physical interrupt side effects are not established.
Saved result: `g2/build/bootloader-completion/mspi-compatible/comparison-first.json`.

Stale source integration bindings were resolved by rebuilding and rerunning:

- `filesystem-owned-compatible/integration-revalidated.json`: PASS 18 calls;
  real littlefs/TLSF/update source, 18 allocations and 18 frees, 58 balanced
  lock/unlock observations, synthetic NOR and image storage.
- `task-integrated-compatible/integration-revalidated.json`: PASS 20 calls;
  real DFU task + filesystem/TLSF/update/handoff assembly. 27 allocations and
  24 frees, with the mounted filesystem retaining three allocations; no leak
  conclusion. 88 balanced lock/unlock observations. Application vectors are
  prepopulated synthetic fixtures; this is not proof of installed hardware boot.

Both results live under `g2/build/bootloader-completion/`; the old results are
retained and superseded, not silently rewritten or counted twice.

Independent queue-wrapper recovery under `inventory-worker/queue-wrappers/`
passed 45 cases and executed 418 original bytes, Cortex-M55 source build.
It fixes a decompiler-inverted context predicate: IPSR nonzero means nonblocking;
thread-mode runtime helper result exactly 1 bypasses mask checks. For other
tested helper values, PRIMASK/BASEPRI determines the nonblocking path. Kernel
calls are synthetic and timeout units remain unverified. The source remains
in its owned analysis directory until component integration.

## Remaining boundaries

Source-complete bootloader and byte-identical bundle are not established.
Missing Linux compiler package/accepted license/activation limits IAR testing.
New compiler 10.10.2 is not the existing stock-candidate 9.60.2. C-SKY supports
CK804 but lacks GX8002-specific SDK inputs; EM v4.6 has not been matched to the
stock v4.2 libraries. Boot kernel, platform initialization, full flash/MSPI
driver and exact build closure remain implementation work. No firmware was
flashed, no hardware accessed and no commits or staging performed.
