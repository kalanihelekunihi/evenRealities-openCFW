# Goodix legacy profile commands in C, 2026-11-11

Stock `0x6249c` and `0x624c8` route selector zero to the existing Goodix
profile switch with argument zero or one respectively. Selector one stops
the stock profiles. Both successful selectors set packet byte 4 to one and
send a five-byte legacy reply. Other selectors return zero without changing
the packet or calling Goodix. The source owner is
`r1/src/application/goodix/native_profile_commands.c`.

The ignored `build/r1-goodix-profile-commands-c-20261111/probe.c` exercises
all 256 selectors for each command with AddressSanitizer and
UndefinedBehaviorSanitizer. All 512 cases pass, including call counts,
profile selection, packet writes, reply lengths, and invalid selectors.
The current strict application link resolves both command symbols; the
underlying Goodix biometric algorithm roots remain separate unresolved work.
