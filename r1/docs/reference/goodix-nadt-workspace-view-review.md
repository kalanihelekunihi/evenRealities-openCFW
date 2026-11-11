# NADT workspace alias for the production RAM owner

The typed `goodix_primitives_nadt_stream_process` implementation for stock
`0x6E008` previously required a 1,400-byte in-struct history workspace.
The production initializer already owns exactly those four banks in
`r1_goodix_native_nadt_workspace`: two 400-byte signed-word arrays, a
200-byte signed-halfword marker array, and a 400-byte signed-halfword
secondary history. The native workspace now declares those element types,
preserving its verified offsets and size. Its
`r1_goodix_native_nadt_workspace_view` function binds the four exact buffers
with no copy. The new non-owning
`goodix_primitives_nadt_stream_workspace_view` lets the existing root execute
on those buffers. The prior API is retained as a wrapper around the same C
implementation; there is one algorithm body.

The ignored host probe
`build/r1-goodix-root-reachability-20261111/test_nadt_view.c` compares the
embedded-workspace API with the view for uninitialized state, a skipped
50-Hz cadence tick, and a prepared 25-Hz active sample. It compares complete
state, output, workspace, configuration, and optical history after each path.
An undersized view is rejected before mutation. This verifies the refactor's
selected behavior, not stock parity or the eventual native-state mapping.

`build/sources-r1-nadt-native-view-fixed-20261111/report.json` compiles 946 application
and 82 bootloader units without failure or duplicate strong symbols. The
bootloader strict link passes. The application receipt
`build/r1-link-nadt-native-view-fixed-20261111/report.json` still has three Goodix imports
and uses 663,720 of 696,320 flash bytes. With all three typed roots and both
HBA/HRV runtime binders and the native workspace binder made reachable by
build-only invalid callers, the ignored size probe links at 690,664 bytes.
Its 5,656-byte remaining flash
margin is provisional: the production calculation adapters and any extra providers are
not in that probe. The view creates no executable blob or second persistent
history owner.
