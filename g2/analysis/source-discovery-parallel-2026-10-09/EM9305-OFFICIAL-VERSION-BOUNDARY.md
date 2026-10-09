# Official EM9305 SDK version boundary — 2026-10-09

Read-only investigation of existing authorized vendor documents and public official endpoints. No duplicate SDK download, compiler/binary execution, credentials, vendor contact or canonical changes. No newly useful public source package was available for acquisition in this bounded search.

## Verified acquisition boundary

Official product page https://www.emmicroelectronic.com/product/standard-protocols/em-bleu-em9305 links datasheets/factsheets and contact, but exposes no v4.2 SDK/port archive. Public developer portal https://forums.emdeveloper.com/index.php?resources/= explicitly invites registration to access all resources/forums; guest view exposes general resources and login/register, not an authentic v4.2 package. Search queries for EM9305 SDK v4.2, EM9305 qf_port.h, EM_BLEU_SDK on GitHub and version-specific official/forum entries produced no official v4.2 headers/libraries or public ARC port history. This is a search result boundary, not proof that EM cannot supply an old package through an authorized account/support channel. No guessed private URLs, authentication bypass or repackaged mirror acquisition attempted.

The acquired official QPC pin416dcec8820b9cdb5827497e645d0d9375db53c6 provides generic6.5.1 implementation; it has no ARC port. A vendor port cannot be inferred from its ARM/generic ports. Existing authorized v4.6 qf_port.h is available locally; original v4.2 source/header provenance remains unestablished. Exact historical SDK archive matches authenticate selected binary provider bodies, not publicly obtainable source.

## Concrete version discriminators from existing vendor notes

Existing vendor ReleaseNotes.rst.txt SHA-256 `7832aa17d62126774c11d01362514862420573fc101c888d29c6dec9c983346a`:

- v4.1 section (starts560): QPC PR8856/8718/8719 added internal hooks (620–622); EM HW API PR8804/8802 removed IRQ_MaskAndSave (629). Internal-hook presence can constrain ancestry to that vendor family, but does not uniquely identify4.2 because later versions inherit hooks.
- v4.2 section (452): controller moved to EMB Mango2.2.0, PR9194/9337; CTE qualified, design244581/deviceQ338654. These version strings/constants are specific finite comparators if present in authenticated stock, but no stock match is newly claimed here. CTE capability/configuration and linked ISO bodies must remain separate.
- v4.3 section includes PR9797 adding RF_HandleInterrupt_Tx (405). Source/symbol/call-target comparison could distinguish an unchanged later radio wrapper from4.2; name absence in stripped stock is not proof.
- v4.4 section PR10507 added IRQ_AreInterruptsEnabled in common/9305/includes/interrupts.h (263); later critical-section additions (231+) can explain changed wrappers. Existing API family agreement is not exact version identity.
- v4.6 (23–26) revised watchdog task and component IRQ priorities; PR12531 (90) fixed priority indexing to align with interrupt numbers. Thus importing v4.6 IRQ priority tables/configuration into stock4.2 is specifically unsupported. A changed table or wrapper can be a real release difference, rather than a compiler discrepancy.

These are source history leads already present in vendor documentation, not source implementation recovery. The report does not transfer v4.6 DWARF structure layouts to4.2.

## Next bounded action / stop condition

Owner can compare stock-bound IRQ wrappers against authenticated v4.6 objects while retaining all mismatches, then test version-specific call/table discriminators above. Authentic4.2 headers/libraries require a vendor-distributed old release with license/provenance and hash; an authorized developer account/support download is the concrete remaining acquisition route. Source for qk_port.s/irq_system_isr may still be absent even from such a package, and commercial MetaWare remains a separate producing-build requirement. Public architecture manuals and generic embARC cannot fill that source gap.

No official4.2 package, publicly licensed vendor ARC port repository or immutable port source history was obtained. No entitlement/access denial was encountered; the portal's guest resource visibility is the observed access boundary.
