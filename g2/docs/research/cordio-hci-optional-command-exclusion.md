# Optional Ambiq Cordio HCI command exclusion

Status date: 2026-08-09

## Result

Six optional HCI command translation units own no stock G2 bytes:

| Translation unit | Definitions | R4 blob | SHA-256 |
|---|---:|---|---|
| `hci_cmd_ae.c` | 25 | `60efed943d278fd8ab78dea32be9bb94a6d60cff` | `9e4dfe58a14c9a0236702c8b043c8a47f9f8dec84a2414e12872b22b470532c6` |
| `hci_cmd_bis.c` | 4 | `485f8cdec92d6115fdb7eee0f41ce20e8fee0840` | `b8e57845a0e2d571c24687aebf7b7ae24b758e3a1381b7f5beb0a2d48c0535c7` |
| `hci_cmd_cis.c` | 5 | `e6ca74337df58b75b61468e6c77656f015a1e30e` | `2bc8db926bbf35d15d3260296344daefff9b378e7fae9d21911f0b6d96cbab63` |
| `hci_cmd_cte.c` | 8 | `063d311dd4a74d0e4fc2fe1ee0393ce6042c6b54` | `2b8b30905c5c156e24fc8a37ad74a968fac2d0071d331859898e2dc1a83eefbd` |
| `hci_cmd_iso.c` | 10 | `320931763b29c13de29e6744a580c6f46775c7a5` | `88971b9b328b477806ea82ab07a941bc05b3dfe10c91139b4057c1a12c4f148e` |
| `hci_cmd_past.c` | 5 | `a2da0214d9c342c80167a6dbd4e7c8c67daa44f2` | `5f73618971b48a42f68f2bcbf877d5deb3c9aaade0322197786f1040a9b4c5a4` |

All 57 definitions are source-only. The inventory comes from the later
official AmbiqSuite R4.4.1 import at AmbiqAI/neuralSPOT commit
`4264b9309e03064ffad13a0468d5d0c1110c5288`; it is a compatibility oracle,
not the historical G2-producing commit.

## Binary proof

Every one of the 57 wrappers makes exactly one mandatory call to
`hciCmdAlloc`. The complete stock image has 45 direct calls to that allocator,
digest `425b3d4fdb753c813da0a790d53b157f29e95a1a491a1e96e5b0470c6abbcac6`.
Forty-four lie inside the already closed shared `hci_cmd.c` object and the
remaining call is the linked `HciLeSetPhyCmd`. No unexplained allocator caller
remains for an optional wrapper.

The image also contains none of the six source filenames. This marker absence
is supporting evidence; the mandatory allocator closure is the primary
exclusion witness. The result does not infer that every newer HCI event parser
is absent—event reception and command emission are separate link surfaces.

The complete name/file ledger is
[`ambiq-cordio-hci-optional-command-exclusion.tsv`](../../tools/manifests/ambiq-cordio-hci-optional-command-exclusion.tsv).
[`analyze_g2_cordio_hci_optional_commands.py`](../../tools/analyze_g2_cordio_hci_optional_commands.py)
pins the authenticated image, manifest, allocation-call digest, closed caller
intervals, and absent markers. The proprietary Ambiq definitions are not
copied or compiled into openCFW; production ownership remains zero.
