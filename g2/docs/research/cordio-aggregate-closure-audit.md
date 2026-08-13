# Cordio aggregate third-party closure audit

## Result

The older **80–85% overall Cordio identification** estimate is superseded for
the reusable Apollo host-stack surface. The authenticated retained-path census
contains 36 Cordio paths: 22 public Packetcraft candidates, five Ambiq ports,
and nine Ambiq/application-or-product paths. Every one of the 27 reusable
stack/port paths now has a focused analyzer and matching test. The repository
also contains 69 focused module analyzers, 69 matching tests, 69 function maps,
and 70 provenance manifests. No retained reusable Cordio path or focused
third-party module remains unclassified.

A copied-path follow-up closes an additional source-ownership blind spot outside
that 36-path `third_party` census. The retained product path
`platform\ble\profiles\gatt\profile_gatt.c` is Packetcraft's six-function
`gatt_main.c` object. Exact r20.05c source/header blobs are now admitted under
Apache-2.0; five functions are direct semantic matches and `GattDiscover`
preserves its upstream terminal call after a local logging expansion. See
[`cordio-gatt-profile-source-recovery.md`](cordio-gatt-profile-source-recovery.md).

A second copied-path follow-up identifies
`platform\ble\profiles\ancc\profile_ancc.c` as AmbiqSuite's ANCC application
profile with G2 extensions. The full object has 21 functions: 12 remain
Ambiq-derived and nine implement G2 message, synchronization, whitelist,
callback, and logging policy. The exact 17-definition AmbiqSuite 2.5.1 oracle
is admitted at public import commit `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`.
Its implementation is identical in authenticated 2.2.0 through 2.5.1 imports,
so this is a selected baseline rather than a claim about the private producing
checkout. See
[`ambiqsuite-ancc-profile-source-recovery.md`](ambiqsuite-ancc-profile-source-recovery.md).

A third product-path follow-up closes the adjacent EUS, ESS, EFS, and NUS
objects in the opposite direction: all 21 linked functions / 2,374 body bytes /
3,000 physical bytes are G2-local Cordio provider adapters. Their shared state
and event topology does not occur in AmbiqSuite's profile set, and the NUS
object does not match Nordic's `ble_nus_*` API. This is a negative dependency
classification, not another source admission. See
[`g2-ble-transport-profiles-recovery.md`](g2-ble-transport-profiles-recovery.md).

The final two retained product-profile paths are now classified too. G2's OTA
object retains four functions derived from AmbiqSuite's stable AMOTA
application skeleton and three product-local actions; selected 2.5.1 source is
admitted as the reproducible oracle. Ring's seven functions are entirely
G2-local. See
[`g2-ble-ota-ring-profiles-recovery.md`](g2-ble-ota-ring-profiles-recovery.md).

The nine `ble-profiles/apps/app` paths are no longer an opaque dependency
boundary. Exact AmbiqSuite 2.5.1 application-framework source is admitted from
public commit `de5c6ba3044f…`, with Packetcraft r20.05c recorded as its public
ancestor. The authenticated stock map pins 50 functions / 29,110 bytes, and a
focused legacy-object pass recovers 14 master/slave functions including two
stored callbacks. Stock's much larger MRAM, privacy, pairing, connection,
diagnostic, and UI delta remains first-party reconstruction work; exact source
identity and production routing are both false. See
[`ambiqsuite-cordio-app-framework-source-recovery.md`](ambiqsuite-cordio-app-framework-source-recovery.md).

The fail-closed reconciliation is implemented by
`tools/analyze_g2_cordio_closure.py`. It composes the authenticated 36-path
source map, checks the 27 path-to-audit dispositions, and rejects analyzer,
test, function-map, or provenance-census drift.

## Origin and version bounds

The aggregate evidence supports four source-oracle classes:

- Packetcraft's public Apache-2.0 Cordio repository, with a bounded r20.05
  through r20.05c interval. The release commits are `eeb34839755d…`,
  `5e21ee596a80…`, `eb4282c7abe7…`, and `3656312d6b73…` respectively.
- Packetcraft r19.02 commit `86372d84ef03…`, used only where an individual
  module or body is proven unchanged or supplies ancestry.
- the later official AmbiqSuite R4.4.1 import in AmbiqAI/neuralSPOT commit
  `4264b9309e03…`, used as a module-specific later oracle rather than a claim
  about the G2 producing checkout;
- official AmbiqSuite R2.5.1 archive SHA-256
  `87b03680c0ac5a5291938e7c522f86146a954d935588f1deb046f35012fe4133`,
  which pins the exact proprietary implementation family for selected WSF
  FreeRTOS ports and the permissively licensed ANCC application profile; the
  latter also has a reproducible public Git import at `de5c6ba3044f…`.
- the public SparkFun AmbiqSuiteSDK 2.5.1 import at commit `de5c6ba3044f…`,
  which supplies the exact nine-file Apache-2.0 application-framework oracle;
  this remains distinct from the private G2 producing checkout.

No single exact historical commit is defensible. The stock host combines r20
behavior and layouts, older unchanged bodies, later-R4/Ambiq interfaces,
proprietary FreeRTOS/HCI ports, and local diagnostic/product patches. The
proper recovered state is therefore a per-module oracle ledger, not one fake
whole-tree hash.

## Residual boundary

The remaining Cordio work is no longer third-party identity or opaque reusable
module classification. It is:

- source admission and final placement of the already selected public or
  clean-room candidates;
- hardware/controller/concurrency validation;
- unavailable private Ambiq producing commits and exact IAR build metadata;
- clean reconstruction of the G2-local application-framework delta, now
  shortcut by the admitted AmbiqSuite source oracle.

Run the audit with:

```sh
python3 tools/analyze_g2_cordio_closure.py \
  --ghidra-corpus /var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth
```
