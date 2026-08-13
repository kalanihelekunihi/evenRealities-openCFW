# Packetcraft Cordio GATT-profile source oracle

This directory admits the two exact upstream files needed to close stock G2's
copied `platform\ble\profiles\gatt\profile_gatt.c` object. Both blobs are
unchanged throughout Packetcraft releases r20.05 through r20.05c; OpenCFW
selects the already-established r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`.

The stock object contains all six `gatt_main.c` functions. Five preserve the
upstream behavior directly. `GattDiscover` adds G2 EasyLogger diagnostics, then
performs the upstream `AppDiscFindService` call with the same arguments. This
is a source oracle only and is not routed into the production overlay.

Run `python3 third_party/packetcraft-gatt-profile/verify_snapshot.py` and
`python3 tools/analyze_g2_cordio_gatt_profile.py` to verify the upstream blobs
and stock object closure offline.
