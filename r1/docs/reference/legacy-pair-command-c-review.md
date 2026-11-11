# R1 legacy pair command in C, 2026-11-11

The locked application command at `0x92b98` sends seven bytes unchanged
for every selector except one. Selector one saves packet byte four, cancels
the two delayed pair callbacks, and reads the current glasses connection
handle. A different active handle logs the conflict, calls the no-op pair
hook with the requested handle, and returns zero without a reply. With no
conflict, a byte-four value other than `0xff` assigns the requested
connection role. If none of packet bytes five through seven is `0xaa`,
the command opens touch service for an ordinary value or closes it for
`0xff`. It then writes one at packet byte four and sends seven bytes.
The C owner is `r1/src/application/board/native_legacy_pair_command.c`;
all delayed-event, role, touch-service, logging and reply dependencies
already have source owners.

The ignored host probe at
`build/r1-legacy-pair-command-c-20261111/probe.c` passed all 256
selectors, a connection conflict with both log sinks enabled, a close
request, and each of the three `0xaa` guard positions under ASan and
UBSan. The R1-only source receipt at
`build/sources-r1-legacy-pair-command-c-20261111/report.json` compiled
934/934 application and 82/82 bootloader units without failures or
duplicate strong symbols. The strict application receipt at
`build/r1-link-legacy-pair-command-c-20261111/report.json` has 17
undefined functions and uses 641,696 of 696,320 flash bytes without
overflow. The bootloader strict link passes. Hardware pairing behavior
and stock byte identity remain unverified.
