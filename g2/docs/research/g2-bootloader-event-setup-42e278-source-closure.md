# G2 bootloader event-runtime setup source closure

The complete setup wrapper at `0x0042E278` and callback dispatcher at
`0x0042E284` are now source-owned MIT C. The first initializes the retained
event runtime and enters the dispatcher. The second performs the authenticated
runtime-value/runtime-call sequence with selectors 8 and 48 around the
callback stored through the retained cell at `0x200004CC`.

Apple clang 21 and Homebrew clang 22 reproduce the authenticated 12- and
30-byte bodies exactly from mnemonic-only Arm source. Portable host tests
exercise ordering, refreshed values, both selectors, and setup-before-dispatch
behavior. Live retained-cell and callback behavior is blocked by unavailable
physical evidence.
