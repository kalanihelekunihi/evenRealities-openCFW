# Cordio dynamic ATT service exclusion audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The optional `atts_dyn.c` TU is not linked into stock G2. All seven source
definitions are source-only/dead-stripped: `attsDynAlloc`, `AttsDynInit`,
`AttsDynCreateGroup`, `AttsDynDeleteGroup`, `AttsDynRegister`,
`AttsDynAddAttr`, and `AttsDynAddAttrConst`.

Both dynamic attribute-add APIs must finish a service by calling the linked
`AttsAddGroup`. Its complete caller set contains eight static service-table
builders and no dynamic-TU body. `AttsDynDeleteGroup` must call
`AttsRemoveGroup`; its sole stock caller is the already-closed CSF/database
path. Thus no dynamic provider reaches either group mutation API. The image
also contains no dynamic ATT source path, symbol/trace marker, HID application
path, or evidence for the TU's 1,280-byte private heap.

Official Packetcraft consumer topology reinforces the closed provider set:
only the HID and battery dynamic service builders use these APIs, and every
builder reaches `AttsDynAddAttr` or `AttsDynAddAttrConst`. Stock instead links
its service groups through static tables.

## Optional source oracle

Packetcraft r20.05--r20.05c and the later official AmbiqSuite R4.4.1 import
share the exact Apache-2.0 file:

```text
blob    a125a644317eb973674637ea6fa0391c13999bf2
bytes   11,119
sha256  fb310af2be69489884b104a35288f3539c2bb47dbc6ebe48d4070e3133cea9d3
```

The r19/AmbiqSuite 2.x file has identical implementation bodies and differs
only in license formatting. No stock body survives to discriminate releases.
Exact source-span hashes are pinned in the function-map manifest.

```sh
python3 tools/analyze_g2_cordio_atts_dyn.py --json
python3 -m unittest tests.test_analyze_g2_cordio_atts_dyn
```

Production ownership and source replacement remain zero. With this exclusion
and the EATT exclusion, every ATT server TU in the selected Cordio family is
now accounted for as linked or source-only.
