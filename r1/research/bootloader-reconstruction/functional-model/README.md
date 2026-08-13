# Compile-tested R1 bootloader functional model

This directory is a clean, host-executable C model of the security- and update-critical behavior
recovered from the live R1 bootloader. It is intended for review, testing, and incremental porting
to nRF52840. It is not represented as the vendor's original source and it is not expected to emit
the captured `0x6000`-byte image.

Implemented behavior:

- reflected CRC-32 using the recovered `0xedb88320` polynomial;
- primary/backup settings reconciliation, including restoration of protected bank, progress,
  init-command, and boot-validation state when the backup is valid;
- ECDSA-P256/SHA-256 init-command authentication through explicit crypto callbacks;
- version, hardware, and SoftDevice policy checks after signature authentication;
- signed-total and `0x1000`-byte DATA object bounds;
- independent full-image SHA-256 postvalidation;
- application/SoftDevice/bootloader activation selection;
- the two application-handoff ACL ranges recovered by the security audit;
- bounded BLE DFU control-point parsing; and
- bounded nanopb varint and advertising-name handling.

The last two items intentionally reject malformed inputs that the captured image reads out of
bounds. They preserve valid-input behavior while repairing the short-read, unterminated-varint,
and advertising-name defects documented in the security audit.

Build and run the tests:

```sh
make -C docs/r1-bootloader-reconstruction/functional-model test
```

The crypto interface is deliberately injected. Production use must bind it to an audited
nRF52840-compatible SHA-256 and P-256 verifier and retain signature enforcement. The model has no
private signing key, unsigned-image acceptance mode, or secure-boot bypass.
