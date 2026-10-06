# P2-15904 candidate ledger gaps

Status: `partial`, `accepted:false`. Private diagnostic reconciliation only; not a function inventory, coverage ledger, or canonical admission.

## Authenticated scope

- 43 target-image records (22 SRAM, 21 XIP); all instruction and pseudocode hashes match. Task-contract hashes bind receipts. Manifest hashes and listed artifacts were checked where the receipt binding matched; the single exception is detailed below.
- Image identities, inventory hash, route-model projection, and mapping evidence hashes were checked. Full guard, bounds, premises, references, and unresolved clauses are embedded in `ledger.json`.

## Missing review bindings

- `P2-csky-recovery-3642/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-3670/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-3706/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-3732/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-3756/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-3782/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-3830/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-3848/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-3866/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-3892/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-3908/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-3928/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-3950/001` (binh_a_stage2_xip): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-3984/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4000/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4056/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4056/002` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4082/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4154/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4210/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4238/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4300/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4314/001` (binh_a_stage2_sram): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4344/001` (binh_a_stage2_xip): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4382/001` (binh_a_stage2_xip): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4418/001` (binh_a_stage2_xip): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4482/001` (binh_a_stage2_xip): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4536/001` (binh_a_stage2_xip): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4606/001` (binh_a_stage2_xip): attempt receipt has no independent_review; reviewer=not named.
- `P2-csky-recovery-4694/001` (binh_a_stage2_xip): receipt names reviewer but review file not found; reviewer=P2-csky-recovery-4695.
- `P2-csky-recovery-4814/001` (binh_a_stage2_xip): receipt names reviewer but review file not found; reviewer=P2-csky-recovery-4815.
- `P2-csky-recovery-4932/001` (binh_a_stage2_xip): receipt names reviewer but review file not found; reviewer=P2-csky-recovery-4933.
- `P2-csky-recovery-4982/001` (binh_a_stage2_xip): receipt names reviewer but review file not found; reviewer=P2-csky-recovery-4983.
- `P2-csky-recovery-5010/001` (binh_a_stage2_xip): receipt names reviewer but review file not found; reviewer=P2-csky-recovery-5011.
- `P2-csky-recovery-5052/001` (binh_a_stage2_xip): receipt names reviewer but review file not found; reviewer=P2-csky-recovery-5053.
- `P2-csky-recovery-5072/001` (binh_a_stage2_xip): receipt names reviewer but review file not found; reviewer=P2-csky-recovery-5073.
- `P2-csky-recovery-5096/001` (binh_a_stage2_xip): receipt names reviewer but review file not found; reviewer=P2-csky-recovery-5097.
- `P2-csky-recovery-5140/001` (binh_a_stage2_xip): receipt names reviewer but review file not found; reviewer=P2-csky-recovery-5141.
- `P2-csky-recovery-5238/001` (binh_a_stage2_xip): receipt names reviewer but review file not found; reviewer=P2-csky-recovery-5239.
- `P2-csky-recovery-5262/001` (binh_a_stage2_xip): receipt names reviewer but review file not found; reviewer=P2-csky-recovery-5263.
- `P2-csky-recovery-5316/001` (binh_a_stage2_xip): receipt names reviewer but review file not found; reviewer=P2-csky-recovery-5317.

Present reviews remain scoped and do not set `accepted:true`.

## Manifest binding exceptions

- `P2-csky-recovery-4056/002` receipt names `g2/build/pseudocode-first/20260930T190500Z/analysis/csky-recovery-4056/001/artifact-manifest.json` with SHA-256 `f352105b716946fc47faf1b9a75dd9ec27c8ed9f519a58d05cf9067e16129e44`; resolved bytes hash to `d81c8f961d200317743a93deec9f587f0e17bec020a27f2d04be815c1748ab45`. No mismatch was repaired or re-pinned.

## Unresolved items

- Index matching is diagnostic byte matching under stated formats/order hypotheses; it does not validate the ISA, prove ownership, or review pseudocode.
- Conditional guards depend on unmeasured/unverified PMU NOR base and route selection. SRAM SPI helper/read-copy success is unverified; XIP aperture mapping/enable is unverified. Full vectors/entry/caller closure, startup alternatives, and executable function completeness remain open.
- Per-attempt semantic unknowns are preserved from receipts, contracts, and pseudocode cue lines. ABI, dispatch, peripheral effects, callbacks, and runtime behavior remain unresolved.
- P2-4056 attempts 001 and 002 remain distinct. 43 counts candidate records, not functions or coverage. Original discontiguous spans remain; merged runs are display aids only.
