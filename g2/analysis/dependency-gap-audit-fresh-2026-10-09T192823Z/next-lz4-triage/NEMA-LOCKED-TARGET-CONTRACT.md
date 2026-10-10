# IAR Nema locked-target comparison contract

Independent in-memory static ar/ELF parsing only; no extraction, tool/firmware execution or binary redistribution. `nema_target.py` and `NEMA-TARGET-BASELINE.json` preserve metadata/hash results. License certification remains discovery's task; this audit does not expand the header license into a binary/source grant.

Archive SHA8c6204496ab53860241db9236487a0eb93badf9627be4eea55249847813827e7 verified. Member nema_cmdlist.o SHA2bbb07808e3e2aca417829dc3edc9a6e78d17c8df69fdce3341088af5e7c2e70; ELF ET_REL/machine40 ARM. Embedded producer IAR ANSI C/C++ Compiler V9.70.1.475/W64 for ARM agrees with discovery. Compiler family is content-bound, not solely a pathname. It does not prove stock used9.70 or exclude unchanged code from an older compiler.

## Primary finite target

Historical locked provenance maps5143D4 to nema_cl_bind_sectored_circular. Independently authenticated locked range5143D4–5144BA:230bytes SHA1b72806af461fbd44dc0a8928e9a4b4493d124242f8f89f7d5820d0c8c692b6d. Historical provenance names are stronger anchors than anonymous link-order labels, but canonical TSV currently classifies this as Unverified/g2-freetype-engine-census; no canonical reclassification was made. Name/extent authentication is not yet an independent algorithm-identity proof.

Candidate symbol ST_VALUE885 (Thumb bit set; instruction offset884), size222, section8 `.text`. Shared section size5644/hash51f3b98557d957b556c2bdb4629e1807170dfee35d9cb04d629aaeaa91199153. Candidate complete symbol bytes SHAe8b0d7c0bc4363c4f2d266fced1ff65764b59e4ec84346ffd8570f191616ddca. Do not call this a separate222-byte section; adjacent symbol/data boundaries matter.

Within selected symbol, three REL relocations occur:

- function+110, type30 ARM_THM_JUMP24, nema_set_error;
- function+114, type54 ARM_THM_PC12, ??DataTable12;
- function+172, type10 ARM_THM_CALL, nema_set_error.

For every relocation, retain original in-place addend/instruction bytes, symbol/table definition and signed offset rules. Bind stock call/tail targets and table cells independently; shared DataTable12 may itself carry relocations to globals. A function-level comparison with these positions masked is similarity only, not byte identity. Every byte of the222-byte symbol must be compared after explicit linkage; separately classify the stock230-byte envelope's extra8bytes as code, literals/alignment or an extent error. Size difference alone cannot exclude the candidate until that classification. Conversely, silently truncating stock to222bytes would lose evidence.

## Secondary boundary controls, not another research branch

Historical rewind514384–5143D4 is80bytes/hashb0733ab3843dc9140923a56f1b4578c87c2ab80483c22d2d42449bc00201c1a6. Candidate nema_cl_rewind has80bytes at instruction offset496, three relocations+14(type30,set_error),+28(type54,DataTable12),+68(type10,set_error). It is a useful layout/control comparator if primary binding cannot classify the extra8bytes, not a license to sweep all members.

Historical get_bound5144FA–514504 is10bytes/hash856d4a249ba795e296531efb875294d949d28902aee69f35217679085b09b0e1. Candidate10bytes has a type54 relocation at+0 to DataTable12. A tiny getter match alone cannot select SDK/compiler version. `nema_cl_bind_circular` candidate168bytes is recorded in JSON, but no independently authenticated named stock range was supplied; do not substitute a guessed address for the primary sectored target.

## Stopping and claims

Discovery should finish one primary symbol comparison with complete text, relocation/table closure, explicit stock envelope and compiler attributes. If only relocation-free islands match, report those bytes and remaining linkage; do not label the entire function exact. If code differs at a verified nonrelocation instruction, exclude this symbol candidate only. If complete linked bytes match, it supplies one authentic binary producer/ABI oracle; it does not supply implementation C, license for retained blobs, GPU/hardware fidelity, archive-wide interchangeability or the exact producing compiler revision. Prior GCC comparisons and common API1.4.12 do not establish those claims.

No original-image execution, canonical coverage increments or production/Git/index changes occurred. The locked main raw hash used is19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701, base438000. Emulator addresses from another firmware profile are not imported.
