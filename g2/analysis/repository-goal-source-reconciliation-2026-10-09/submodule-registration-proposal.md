# Comparison-reference registration proposal

Proposal only. No root Git metadata or registry was changed. Acquisitions and
per-file provenance are owned by `source-discovery-parallel-2026-10-09`.

| Proposed path | Public URL | Exact pin | Scope |
| --- | --- | --- | --- |
| `third-party/reference/embarc-osp` | `https://github.com/foss-for-mips-arc-processors/embarc_osp` | `67ea926c6a62aa6e19efdc3b11cba3ea0b467e29` | ARC semantics comparison; no stock linkage attribution |
| `third-party/reference/nationalchip-lvp-aiot` | `https://github.com/NationalChip/lvp_aiot` | `d4aa00943e22f9ddfa424f979fae3ee2a62f5c0b` | Alternate GX8002 provider/board comparison; no producing-checkout attribution |

Proposed `.gitmodules` entries, to apply only in a separately authorized Git
registration operation together with exact gitlinks:

```ini
[submodule "third-party/reference/embarc-osp"]
    path = third-party/reference/embarc-osp
    url = https://github.com/foss-for-mips-arc-processors/embarc_osp
    shallow = true
    update = none
[submodule "third-party/reference/nationalchip-lvp-aiot"]
    path = third-party/reference/nationalchip-lvp-aiot
    url = https://github.com/NationalChip/lvp_aiot
    shallow = true
    update = none
```

Registry wording should retain root BSD-3-Clause / MIT license qualifications
and per-component terms. Neither acquisition counts as recovered executable
coverage, a firmware dependency, or an authenticated original build input.
