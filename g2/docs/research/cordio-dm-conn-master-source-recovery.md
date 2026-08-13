# Cordio DM master-connection source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

Five of six `dm_conn_master.c` functions survive in
`[0x0055BC5C,0x0055BCE8)`: 138 code bytes plus two alignment bytes form a
140-byte physical span, SHA-256
`f894567b3ff7e8656db0f7aa655f7d200039dd54d4e4e57eb3be48e559b99940`.
`DmConnSetAddrType` is dead-stripped; its only public consumers belong to the
already-proven absent `dm_dev_priv.c` module. Two direct calls, three stored
entry pointers, and zero strict-interior pointers close ingress.

Stock decisively selects Packetcraft r20/Ambiq R4 architecture. The retained
`DmL2cConnUpdateInd` writes event `0x72` for component 14 and calls the
separate `dmConnUpdExecute`; r19 instead writes `0x35` and calls the old
unified `dmConnSmExecute`. The owned two-entry update table at
`[0x0078D41C,0x0078D424)` hashes to
`2e09ae0bb88caae24d3c82a9f6dc43f556582c9598102685b23b746fde39e6e7`.

The selected Apache-2.0 source is Packetcraft r20.05c blob
`d92f3e7ee4f64b27799337fb421198fda14f55a3`, 5,337 bytes, SHA-256
`8555ab595045465c0ae6ef018a5af41d9003fd40e942e4b69ef42eb326a02ca0`.
Official Ambiq R4.4.1 is byte-identical later corroboration, not a historical
producing-commit claim.

The linked actions cancel connection creation, submit master and L2CAP-driven
connection updates, translate L2CAP update indications, and open a master-role
connection through `dmConnOpenAccept`. Their two direct callers are exact
retained `l2c_master.c` and `app_master.c` bodies. The registered action
pointers are installed by the independently bounded `DmConnMasterInit` path.

The verified readiness archive is
`research/readiness/dm-conn-master/`, 5,913 bytes,
SHA-256 `ea9dea68612c879dd6adff94e24b34bd0a3a3c67ce3f8ca1864544f5033f9356`.
Its fifteen inner hashes cover six functions, seventeen source inputs, ten
provider seams, and two live Os/O1 zero-unresolved links. Licensed source and
build products are excluded.

```sh
python3 tools/analyze_g2_cordio_dm_conn_master.py --json
python3 tools/verify_research_corpus.py --json
```

Production replacement remains zero. The now-authenticated action-table
topology makes `dm_conn_master_leg.c` the next strongest bounded target.
