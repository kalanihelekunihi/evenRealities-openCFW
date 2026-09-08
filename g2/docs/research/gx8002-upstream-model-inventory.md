# GX8002 upstream model exclusion screen

Date: 2026-09-07. The pinned NationalChip SDK's public model declarations were
inspected as a route to recovering the codec's remaining neural-network data
and connected runtime source.

`analyze_gx8002_upstream_models.py` authenticates SDK commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, each selected model header's Git blob,
and the official codec hash. It inventories declared byte-array lengths and
model identifiers without compiling, emitting, or admitting any model arrays.

The [report](gx8002-upstream-model-inventory.json) covers 17 model headers,
including hybrid XIP variants. None has the codec's pair of 9,164 command bytes
and 120,800 weight bytes. This is a size-based exclusion screen for direct
reuse, not a proof of model semantics or a search of every historical SDK
revision. No unrelated wake-word model has been substituted.

The SDK models do provide typed input/state/output buffer layouts, compiler
metadata and task setup C. `lvp/common/snpu_engine/lvp_kws.c` also shares several
runtime diagnostic strings with the codec. These are useful next boundaries:
recover the actual model task, buffer shapes and runtime configuration, then
understand the command stream and tensor roles. An upstream byte array alone
would not satisfy the active goal's requirement for understood, maintainable
functionality and data.

The restored upstream source remains under `build/upstream-nationalchip-lvp-kws`.
The firmware builder does not consume these model arrays. The codec's model
and accelerator regions remain source-incomplete.
