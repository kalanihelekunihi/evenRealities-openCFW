# R1 SDK authorization adapter in C

The stock SDK authorization root at `0x8EA0C` now has one application owner,
`native_health_auth_parameters_set.c`, listed in `r1/src/sources.json`. It reads
the existing cached identity and pKey providers, normalizes the UUID through
the typed GoMore parser, decrypts the token through the source-owned two-pass
AES wrapper, then dispatches four fields through the previously reconstructed
GoMore primitives. The two 32-byte decrypt key records are source-owned
non-executable data. The shared 20-byte status record remains at the existing
`r1_gomore_runtime_configuration` owner.

The ignored probe `build/r1-auth-record-owner-20261111/inspect_full_auth.py`
executes the locked `r1-2.2.6.0009` application with its startup decompressor
and cached identity path. Its complete return and status record match the host
C adapter for five paths:

| Path | Return | 20-byte status |
| --- | --- | --- |
| Valid cold token | `0` | `00f153653700000000a4f6a00000000004000000` |
| 23-character cached UUID | `-1005` | `00000000ffff0000000000000000000000000000` |
| Corrupted but valid Base64 token | `-1002` | `0000000016fc0000000000000000000000000000` |
| Valid token, timestamp `0` | `0` | `000000005f00000000a4f6a00000000004000000` |
| Valid token, timestamp `UINT32_MAX` | `0` | `ffffffff7900000000a4f6a00000000004000000` |

The host driver is `build/r1-auth-record-owner-20261111/full_auth_host.c`.
This comparison exposed two prior primitive errors: the special identifier's
template branch was reversed, and UUID validators treated the descriptor's
pointer bytes as inline UUID characters. The corrected primitives now read
the typed descriptor, including its timestamp, so host and 32-bit target
layouts use the same fields. The stock optional time check is disabled by the
source-owned `gomore_primitives_return_zero` predicate, as in the locked
routine. The separate final-field probe still passes 100 direct stock/host
C/production Arm comparisons.

`build/sources-r1-full-auth-20261111/report.json` compiled 946 application
and 82 boot units with no failures or duplicate strong symbols. The strict
application receipt `build/r1-link-full-auth-20261111/report.json` reduced
undefined functions from eight to seven, with no flash overflow. The adapter
has not been run on a physical ring. Its source-level behavior and these
selected stock paths do not establish byte identity or complete firmware
integration.
