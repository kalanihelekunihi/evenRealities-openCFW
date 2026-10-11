# Foundation source compilation inventory

COMPLETE bounded compilation inventory: all 40 non-simulator C translation units compile; 11 simulator fixture units are explicitly excluded. Touch SCB units use Cortex-M0+; Apollo units use Cortex-M55. The real critical implementation is selected with `OPENCFW_REAL_CRITICAL`. No fixture providers are compiled into this inventory.

Run `python3 g2/analysis/foundation-source-inventory-20261010/rebuild.py` to replay the sealed commands with compiler/input/object hash checks. The repeat build passed for all 40 objects; `rebuild-receipt.json` records their identities.

`inventory.json` records each actual compile command, source and full include hashes, compiler identity, object hash and GLOBAL/WEAK symbol inventory. Objects are separate outputs under `g2/build/foundation-source-inventory-20261010`; no aggregate target archive or provider binding is asserted. Existing foundation module provenance and original/source comparisons remain the authoritative semantic scope. This pass adds compilation evidence only.

Remaining work is target-specific provider/ABI matching, state ownership and coherent linking. There are 40 candidate units for that review; it is not a count of 40 unresolved firmware functions. Whole-image work cannot be estimated from this inventory.
