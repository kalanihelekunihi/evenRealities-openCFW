# FlashDB 2.1.1 source snapshot

This is a byte-exact, production-excluded copy of the source files openCFW
selected from the official FlashDB `2.1.1` lightweight tag at commit
`714d6159e7e6afb267a3953756abca445c350e61`. The recovered in-image version and
configuration evidence does not prove that Even used this historical checkout
unchanged or without local patches. The snapshot contains only the KVDB core,
its public headers/configuration template, and the generic FAL core needed by
the recovered minimal build. TSDB source, file mode, RT-Thread glue, shells,
demos, and sample device ports are intentionally excluded. Static evidence
proves no live/retained TSDB subsystem, but does not prove whether the original
`FDB_USING_TSDB` macro was defined before linker garbage collection.

`g2-config/fdb_cfg.h` is openCFW-owned recovered configuration and is not an
upstream file. The upstream `inc/fdb_cfg.h` remains byte-exact as a reference
template. No file in this directory is registered in a production overlay.

Run `python3 third_party/flashdb/verify_snapshot.py` for offline provenance,
commit-to-tree-to-path-to-blob membership, source-byte, G2-image, layout, and
configuration verification.
See `docs/research/flashdb-configuration-recovery-audit.md` for the evidence
and the read-only-first promotion plan. That audit now also recovers the two
default-KV node arrays and all 21 default values: twenty from authenticated
initialized SRAM and the zero `kvbooCount` word from the reset-called IAR zero
scatter. Its read/increment/write lifecycle and the eleven first-party
migration callbacks are bounded too, along with the database mutex callbacks,
first-party magic/reset policy, and exact NOR callback return conventions.
Application structure semantics and the golden external-flash oracle remain
unresolved. In particular, do not copy the
stock zero-on-device-failure port behavior: upstream FlashDB treats only
negative FAL returns as errors.
