# Packetcraft Cordio r20.05c source oracle

This directory is an authenticated, production-excluded source-oracle
snapshot from the official Packetcraft Cordio repository at commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6` (commit subject `r20.05c`, tree
`0a76c7dde46d3b94bb9185a4a5327d0e3f38ec97`). It is licensed under
Apache-2.0; the exact upstream `LICENSE.md` is included.

The selection is an openCFW compatibility choice. It is **not** a claim that
the G2 firmware used this exact whole tree. The firmware audit proves
r20.05-or-later behavior for independent ATT and DM functions, and the five
audited source blobs are unchanged from the Packetcraft `r20.05` release
commit through `r20.05c`. G2 also carries local trace differences and an
Ambiq FreeRTOS WSF port, so the function-level equivalence interval cannot be
promoted to a whole-tree identity.

## Included closure

The snapshot contains 41 exact upstream files:

- five source oracles: `atts_csf.c`, `dm_conn_sm.c`, `smp_db.c`, `app_db.c`,
  and the public bare-metal `wsf_buf.c` comparator;
- the 35 transitive upstream headers selected by preprocessing those five
  translation units with Packetcraft's include ordering; and
- `LICENSE.md`.

This is enough to compile the five upstream translation units as reference
objects. It is not a linkable BLE stack and none of those translation units is
registered in an openCFW production build. The production overlay may cite the
snapshot only as provenance for the pinned local `dm_sec`, `dm_sec_lesc`,
combined `dm_sec_slave`/`dm_sec_master`, and product-configured `smp_db`
and patched-r20 `smp_main`, `smp_sc_main`, and `smp_act` adapters; the offline verifier
admits those exact eight-, seven-, six-, eleven-, twenty-one-, and
eighteen-, and twenty-five-function contracts (96 production leaves total,
including one exact in-place `smpActNone`) and rejects direct
snapshot compilation or any broader production reference.

`g2-patches/smp_main-ambiq-aes-queue-cleanup.patch` is repository metadata,
not a sixth vendored upstream source. It applies to the authenticated
r20.05c `smp_main.c` blob in an external exact checkout and records the
independently observed Ambiq stale-AES queue cleanup. Its identity and patched
result are guarded by `tools/analyze_g2_cordio_smp_main.py`; the snapshot
verifier permits the patch file and the exact local 21-leaf `smp_main` and
18-leaf `smp_sc_main` and 25-function `smp_act` production adapters, but does
not count them among the 41
upstream files.

`ble-host/sources/stack/cfg/cfg_stack.h`,
`ble-profiles/include/app_cfg.h`, `wsf/include/wsf_buf.h`, and
`wsf/include/wsf_os.h` are upstream reference templates. Only the facts in
`g2-config/cordio_recovered_config.h` are proven for G2. In particular, the
public sample `APP_DB_NUM_RECS=3` must not be mistaken for the G2 product
database: the recovered Even MRAM layer has ten records and different
persistence semantics.

## Explicitly outside this snapshot

- Ambiq FreeRTOS WSF and HCI transport ports, including the unavailable G2
  `wsf/sources/port/freertos/wsf_buf.c` derivative;
- Even `platform/ble`, MRAM persistence, services, profiles, policy, and
  callbacks;
- controller/radio firmware and platform hardware support;
- the rest of the Packetcraft host, profile, WSF, mesh, controller, examples,
  build system, and tests.

The bare-metal `wsf_buf.c` is useful for algorithm comparison only. It must
not replace G2's FreeRTOS port until scheduling, critical-section, allocation,
ABI, and call-closure behavior have separately been proved.

## Verification

The verifier is completely offline. It hashes every selected file and its
canonical Git blob, reconstructs every required Git tree from complete entry
lists, reconstructs the pinned commit object, checks the license, verifies the
bounded G2 configuration evidence, and rejects extra files.

```sh
python3 third_party/cordio/verify_snapshot.py
python3 -m unittest -v tests.test_cordio_snapshot
```

See `docs/research/cordio-version-recovery-audit.md` and
`tools/analyze_g2_cordio_version.py` for the authenticated firmware evidence.
