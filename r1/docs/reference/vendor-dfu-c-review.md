# Vendor DFU validation through the C bootloader

This review tests the final GNU-linked bootloader from
`build/sources-goal-r1-boot-ecc-complete-c/report.json` against preserved official
R1 DFU packets. It changes no firmware source or security policy and performs
no device writes.

## Positive signed-packet evidence

All 14 `r1/blobs/official/*/application.dat` files, from 2.0.3.0013 through
2.3.2.0007, verify independently with Python cryptography and with the linked
bootloader's actual `nrf_dfu_validation_signature_check` function. The ELF's
unchanged recovered R1 public key is the trust anchor in both checks.

The signed bytes are the raw protobuf **InitCommand** payload, not the enclosing
Command or Packet encoding. The SDK callback captures this span when decoding;
the signature's r/s limbs and stored public-key coordinates are little-endian
on the wire, and the actual SDK crypto path performs its normal conversions.
No signature, key, digest, protobuf or memory-copy implementation is mocked.

For each packet, the probe runs the actual command-create, append and
`stored_init_cmd_decode` functions with append chunk sizes 1, 31 and the whole
packet. All 42 ingestion cases pass. The decoder-captured signed pointer and
length match an independent wire-format parser, and the signature-check call
uses the actual nanopb-decoded signature bytes from `m_packet`.

Three mutations per packet—one signature-bit change, one signed-payload-bit
change and reversed r/s limb byte order—are rejected independently and by the
bootloader (42 cases, INVALID_OBJECT=5). These mutations remain structurally
valid protobuf, so rejection exercises authentication after decoding.

Additional checks reject missing signatures, a wrong signature type, short and
long signatures, zero/oversized command creation, and append overflow. Truncated
packets and packets containing both signed and unsigned commands fail decoding.
The JSON receipt records the actual results and total call count.

## Full reference application hash

`firmware-hash.py` reads the signed 2.2.6.0009 InitCommand's image size and
SHA-256 field, independently verifies both against the preserved application
binary, and maps that binary as data at its normal 0x27000 flash address.
The linked bootloader's actual `nrf_dfu_validation_hash_ok` accepts all 646408
bytes. Changing one middle image bit causes rejection. Both the digest endian
conversion and the full source SHA-256 implementation execute in the ELF.
The image is read as hash input; this is not application execution.

## Scope and reproducibility

The scripts and raw receipts live in `build/goal-r1-vendor-dfu-c/`. The adjacent
JSON review records packet hashes, final ELF hash, probe hashes, full-image hash
results and input/output evidence. The probes execute the final ELF in Thumb
emulation with its FLASH/RAM/UICR segments loaded. Peripheral access, radio
transport, real flash programming and physical clocks are not exercised. Logging
remains in its uninitialized emulator state; no log backend is initialized.

These results close the positive vendor-signature and image-hash checks for this
ELF. They do not exercise complete `init_cmd_execute`/prevalidation, version and
SoftDevice policy, cache placement, activation, real settings persistence or
power-loss recovery. Those remain separate hardware/integration gates. No device
was flashed, no bundle published, and firmware completeness remains unproved.
