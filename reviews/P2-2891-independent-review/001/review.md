# Independent review 2891

Status: **PASS_SCOPED** (`accepted: false`).

The isolated verifier passed and reproduced one function record, five literal-data records, and five analysis-memory records. Candidate artifact hashes match. The function record's source/body identity, mapping equation, and pseudocode pin are consistent; its stable identity is `apollo_bootloader:flash:flash:00429da4:thumb`.

The review binding is exact: review 2835/002 names the same candidate directory, its function JSON hash matches the pinned `function.json`, and its candidate receipt hash matches. The function's four upstream input hashes also match their files. For each of the five data records, I compared the address and value with the pinned original bytes and its referencing instruction in the pinned 2796 instruction listing; all PC-relative literal addresses, words, and four-byte hashes agree. The five interface records correspond to the function's listed ordered RAM/MMIO references and reuse its pinned pseudocode and stable function identity.

These records are private, accepted-false proposals. Their interface entries explicitly remain analysis-only rather than C contracts; physical peripheral semantics and global ownership of the literal ranges remain unresolved. No canonical ledger or admission is changed.
