# EM9305 timer wrapper version comparison

Finite question: are the two stock-bound timer wrappers unchanged in the authenticated available v4.6 ELF? Stop at exact raw mismatch; do not normalize unrecorded relocations or transfer v4.6 IRQ/type configuration to stock.

Both stock payload slices independently reverify discovery's digests. Section-aware ELF reads identify Timer0 at0x3065D0 and Timer1 at0x306694, each194bytes. Stock Timer0[0x305B1C,0x305BDE) and Timer1[0x305BE0,0x305CA2) are also194bytes. Neither pair has equal bytes/digests. Exact hashes are in results.json. No vendor byte arrays, source or type layouts were exported, no compiler or physical execution occurred.

These are failures of unchanged linked-body comparison, not proof of source-level changes: changed call addresses or other linked constants can differ even for unchanged source. No recorded object relocations were available in this ELF-only comparison, so no relocation normalization is claimed. The raw mismatches remain evidence; equal lengths do not prove equivalent frame or timer semantics. Producing v4.2 object/source or authenticated relocatable providers are needed for a justified next comparison.

Existing official version-boundary notes identify v4.1 QPC internal hooks, v4.2 Mango2.2.0 and later critical-section/radio changes; v4.6 specifically changes IRQ priority behavior. These provide possible version discriminators but are not explanations proven for these two mismatches. Existing exact SWI1 and queue-initializer matches cannot authenticate all other v4.6 routines or their layouts. Vendor ARC port, compiler/configuration and stock IRQ priority state remain unknown. Discovery separately owns opcode-source search.

Authentic v4.2 package was not obtained by the bounded public search; the official portal requires registration for resources. An authorized vendor-supplied historical package with license/provenance/hash is the concrete acquisition boundary. This does not prove the vendor cannot supply it or that all in-image static work is exhausted. No credentials/access bypass, Git/production/device/canonical changes.
