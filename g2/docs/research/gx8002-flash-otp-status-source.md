# OTP lock-status candidate

Recovered runtime_gx8002_flash_otp_status.c from authenticated package0x15af4,
runtime0x10023ae0. Native macOS C-SKY build fits68/68 bytes, with the original
16-byte saved-register frame. Not admitted to the firmware candidate.

The routine snapshots descriptor flags through selected_device+20, flags+16,
then waits ready. It reloads selected_device and reads the signed manufacturer
halfword at+6. Only0x5e and0x85 proceed to read status2; others return-1 without
writing caller output. For supported devices it writes the one-bit value at
position(flags&7)+3 and returns0. The output is one byte.

Source uses unsigned shift while stock uses ASR; at shift distances3..10,
masking the result to one bit selects the same original bit for all32-bit
inputs. Compilation uses LD.H plus SEXTH in place of stock LD.HS. Both
observations require decoded qualification, including helper clobbers,
selected-device changes across the wait, unsupported manufacturers, output
aliasing, and full status/region boundaries. No physical OTP operation.

Decoded stock/source comparison now passes28200 cases: all256 low-byte status
values, individual bits8..31 and signed extremes; ten flag patterns; five
manufacturer values; two clobber seeds. The selected-device pointer changes
across the modeled wait, ensuring the reload is used, while the region flags
remain from the original descriptor. Reads and calls are ordered, output byte
and return match independent bit-selection expectations, and the16-byte frame
and saved registers are checked. Four rejection tests cover wrong frame,
wrong helper, premature output and unknown instructions. Admission remains
pending; helper implementations are modeled and no hardware was exercised.

Prepared OTP-status admission adapter and regenerated reviewed verification
report successfully. It requires size fit, decoded comparison and source/header
hash evidence; still not registered in the integration builder. Registration
and full integration are next. Current verified package has111 functions.

OTP status integrated into the full experimental package. Native macOS codec
build passes198 tests; full build and verify-artifacts pass under apple-clang.
Ownership:7120 C,2040 source data,80 metadata,302 fill,316550 retained bytes;
112 functions/128 code occurrences plus16 data regions. Codec SHA-256:
f1f109b0c7f1fb9eb6fe837a8b67bc58ddbba2e98f27d120ec1332c4c2a113d7.
Package SHA-256:6374fd9287ce5049798221df2f5963a6ecf08d12810eb06ed2345611dcc5acb4.
Candidate hash pin does not imply vendor-byte identity or hardware validation.
The source-only goal remains active; no hardware operation was performed.
