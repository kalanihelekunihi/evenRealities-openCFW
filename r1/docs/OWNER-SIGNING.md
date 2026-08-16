# Owner-signing OpenR1 firmware

OpenR1 can be packaged as an owner-signed Nordic Secure DFU application for an R1 bootloader whose
trust anchor is the SybilSight owner key. This does not alter the application image and does not
embed the private key: it creates an `application.dat` init packet containing an ECDSA P-256
SHA-256 signature, then bundles it with the application binary.

## Key custody

The local encrypted private key is
`r1/config/r1-owner-signing/r1-owner-private.key`. It is mode `0600` and explicitly ignored by Git.
Its random passphrase remains in macOS Keychain under service
`com.sybilsight.r1-owner-signing`; the signing tool reads it directly. Public material and
fingerprints remain reviewable beside the ignored private key.

Two byte-identical encrypted private-key copies and matching public-key copies are retained outside
OpenCFW:

- `~/Repo/SybilSight/Config/r1-owner-signing/`
- `~/Repo/apis/secrets/r1-owner-signing/`

The expected SHA-256 of the bootloader-format 64-byte public key is
`03a3d417e1b0071ae436798fa821f03d2d3458eb24959494516e2a1a7e040d0c`. The packager fails closed if
the local private/public pair, raw public key, file permissions, or this fingerprint do not match.

## Build and sign

After configuring the pinned SDK/vendor roots described by the normal OpenR1 build, run:

```sh
make -C r1 sdk-owner-dfu \
  SDK_ROOT=/absolute/path/to/nRF5_SDK_17.1.0_ddde560 \
  BMA456_ROOT=/absolute/path/to/BMA456_SensorAPI \
  LIS2DW12_ROOT=/absolute/path/to/lis2dw12-pid \
  ST25DVXXKC_ROOT=/absolute/path/to/ST25DVxxKC \
  TINY_AES_ROOT=/absolute/path/to/tiny-AES-c \
  FLASHDB_ROOT=/absolute/path/to/FlashDB \
  GOODIX_DEMOCODE_ROOT=/absolute/path/to/gh3x2x
```

If the SDK image already exists, `make -C r1 owner-dfu` signs it without rebuilding. Output is
written beneath `r1/build/owner-dfu/`:

- `openr1-application.bin`: the exact application bytes that were signed;
- `openr1-application.dat`: the signed Nordic init packet;
- `openr1-owner-signed.zip`: the Secure DFU package; and
- `manifest.json`: hashes, versions, public-key fingerprint, and successful signature verification.

The signer refuses to overwrite a non-empty output directory. Use `make -C r1 clean` after
preserving any package you need, or set `OWNER_DFU_OUTPUT` to a new build directory.

Defaults reproduce the owner-keyed R1 package policy already proven by SybilSight: hardware version
`52`, SoftDevice requirement `0x0100`, application version `3`, generated-CRC boot validation, and
the debug version policy. Override these only when the installed owner bootloader's compatibility
policy is known. `OWNER_DFU_APPLICATION_VERSION`, `OWNER_DFU_HARDWARE_VERSION`, and
`OWNER_DFU_SD_REQ` are Make variables; `--enforce-version` is available when invoking
`r1/tools/sign_r1_firmware.py` directly.

The tool only creates and verifies artifacts. It does not connect to or flash a ring.
