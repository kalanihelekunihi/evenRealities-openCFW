# R1 manager version log in C

`r1/src/application/runtime/native_manager_logging_start.c` supplies the
previously missing manager startup log at stock `0x91504`. The pinned stock
routine parses `2.2.6.0009`, formats `VER22609`, and submits it with marker
`0x8c400000` and format `%s`. The C routine reads the existing source-owned
version string and calls the existing typed logger dependency.

The first C draft used `sscanf`, matching the stock call directly. In the
current GNU link it pulled in a large newlib scanner and increased the FLASH
overflow from 189,312 to 238,376 bytes. The retained implementation uses a
bounded four-field decimal parser for the fixed product-version format. It
keeps the fallback `VER%s` path for malformed strings and has no new scanner
dependency. Normal and malformed-version host fixtures pass with AddressSanitizer
and UndefinedBehaviorSanitizer under `build/r1-current-20261110/`.

`build/r1-manager-log-bounded-c-20261110/report.json` compiles all 950 R1
units and composes both payloads with no failed units or duplicate strong
symbols. The application has 59 relocatable imports, down from 60. The strict
GNU link reports 51 unresolved references and 189,584 bytes of FLASH overflow.
This is source/host behavior evidence; startup scheduling, log transport,
complete application linking and physical boot remain unverified.
