# AmbiqSuite AMOTA source oracle

This directory admits AmbiqSuite 2.5.1's AMOTA application source and API
headers as a provenance/architecture oracle for G2's retained
`platform\ble\profiles\ota\profile_ota.c` object.

The stock object is not a pristine build of `amota_main.c`. It preserves the
distinctive AMOTA `0xA0` reset and `0xA1` disconnect message assignments, the
CCC event/diagnostic, handler/dispatcher structure, and the AMOTA/AMOTAS split,
but replaces the actions with an Even OTA control block, event `0xA7`, and a
separate product service provider. Four stock functions retain the Ambiq
skeleton and three are G2-local adapters. No source is production-routed.

The complete upstream file changes at every authenticated 2.2.0–2.5.1 import,
while `amotaProcCccState` and the discriminating skeleton above remain stable.
The binary therefore identifies the lineage but cannot select an exact private
checkout. OpenCFW selects 2.5.1 because its official archive and public import
are already authenticated for the surrounding Cordio tree.

All files retain Ambiq's BSD-3-Clause-style notice. Run
`python3 verify_snapshot.py` to authenticate the snapshot.
