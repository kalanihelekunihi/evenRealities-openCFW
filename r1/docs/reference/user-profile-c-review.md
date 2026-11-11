# R1 profile command callback in C

The system command table's `0x0004` callback now points to the C implementation
`r1_user_profile_handler` in `r1/src/application/runtime/native_user_profile_command.c`.
It calls the existing profile command kernel with a 24-byte local frame; the
former `naked` assembly wrapper is removed. The table declaration now has the
callback's real two-argument signature.

Stock `0x84a10` publishes 12 bytes after assigning only 10 of them in its
stack frame. The C entry zeroes its scratch frame before the kernel runs, so
the final two transmitted bytes are defined as zero. This is an intentional
behavioral choice for previously unspecified bytes, not a byte-identity claim.

The ignored host fixture at `build/r1-current-20261110/profile_callback_test.c`
passes under AddressSanitizer and UndefinedBehaviorSanitizer. It checks four
profile combinations and the missing-payload branch, including the command
reply fields and the complete 12-byte event record. The normal R1 source build
at `build/r1-profile-c-20261110/report.json` compiles all 949 units, composes
both payloads without duplicate strong symbols, and reduces application
imports from 62 to 61. The strict application link then has 53 unresolved
references and a 188,592-byte FLASH overflow. The bootloader source graph is
unchanged. Physical BLE behavior and a final application image remain open.
