# R1 health settings command in C

`r1/src/application/runtime/native_health_settings.c` now supplies the
registered `r1_health_settings_plan_command` and both KV helper entries with
ordinary C wrappers around their existing C kernels. All three handwritten
`naked` assembly frames in that file are removed. The command table declares
the actual two-argument callback type.

The C wrappers zero their private record and command frames before use. This
defines bytes left unspecified by the old stack frames if a KV read fails or
does not fill the full record; successful full reads retain their prior fields
and call sequence. The ignored host fixture at
`build/r1-current-20261110/health_settings_callback_test.c` passes under
AddressSanitizer and UndefinedBehaviorSanitizer. It checks the get response,
unchanged set, changed set with persisted flag/word and event publication, and
missing-payload return.

`build/r1-health-settings-c-20261110/report.json` compiles and composes all
949 R1 units without failures or duplicate strong symbols. Application
imports fall from 61 to 60; strict final-link unresolved references fall from
53 to 52. The application still exceeds FLASH by 189,312 bytes. This work
does not establish physical KV persistence, BLE delivery, or an executable
application image.
