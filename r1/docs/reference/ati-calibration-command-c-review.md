# R1 ATI calibration command in C, 2026-11-11

`r1/src/application/board/native_ati_calibration_command.c` implements the
11 stock selectors of `0x6210c` and its two short state accessors at `0x72898`
and `0x93414`. Selectors zero through two set the ATI report mode or post
touch task flags with the stock structured and SDK log gates. Selectors three
through six send zeroed 44-byte task messages with the observed type, subtype
and payload bytes, then post their touch flags. Selector seven reads two ATI
bytes from the existing factory touch state and sends a six-byte reply, or a
five-byte `0xff` status if that accessor fails. Selectors eight and nine open
or close touch service for source two; selector ten returns the decoded SN
letter. All other selectors preserve the caller packet and send five bytes.

The ignored host probe at `build/r1-ati-calibration-c-20261111/probe.c`
checks all 256 selectors, task message contents, status lengths, mode bounds,
both ATI data accessor null cases, and structured/SDK log gates. It passes
AddressSanitizer and UndefinedBehaviorSanitizer. The probe mocks touch,
logging and transport providers; physical ATI calibration remains unverified.

`build/sources-r1-ati-calibration-c-20261111/report.json` compiles 937/937
application and 82/82 bootloader units with no known failures or duplicate
strong symbols. The strict application receipt at
`build/r1-link-ati-calibration-c-20261111/report.json` has 14 undefined
functions and uses 643,232 of 696,320 flash bytes without overflow. The
strict bootloader receipt at
`build/r1-boot-link-ati-calibration-c-20261111/report.json` links with a valid
vector. Byte identity is not established.
