# R1 owner-signing key

This directory is the local trust root for packaging OpenR1 as an owner-signed Nordic Secure DFU
application.

- `r1-owner-private.key` is the encrypted PKCS#8 P-256 private key provisioned from SybilSight. It
  must be mode `0600` and is explicitly excluded by the repository `.gitignore`.
- `r1-owner-public.pem` and `r1-owner-public-x-y-le.bin` are the matching public key in standard PEM
  and the R1 bootloader's 64-byte little-endian `X || Y` representation.
- `manifest.json` records non-secret fingerprints and encoding metadata.

The passphrase remains in macOS Keychain under service `com.sybilsight.r1-owner-signing`. The
packager reads it directly and never writes it to the repository, command line, package, or build
manifest. The encrypted private key is also backed up under
`~/Repo/apis/secrets/r1-owner-signing/`.

See [`../../docs/OWNER-SIGNING.md`](../../docs/OWNER-SIGNING.md) for the build and custody workflow.
