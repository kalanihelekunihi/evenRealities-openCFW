# Independent FlashDB configuration-probe audit

Ten ARM32 compile probes independently rebuilt into this audit directory with exact emitted constants; eighteen checks passed. Three original-byte receipts match independently extracted locked header-bearing main payload ranges: get_kv5444F4 length86 hash08d04147e072358baf647e0d31880fab0cc0af17ae72b4e8401110a4091593c7; get_blob54454A length104 hash03a3cfe2718933bc5462526c4871406610ef93f5f36dbe768ad7abccc998c254; write_kv_hdr5445B2 length64 hash64e0e31043d90579a349a5aabee831779b7fda09137e093119cb57e1752224c9. Source hashes and pinned714d6159e7e6afb267a3953756abca445c350e61 receipt URLs match; disk-header structure is verbatim. Sources/evidence were read only, all output audit-owned, no canonical admission or Git mutation.

## Exact discrimination

The matrix varies two enum representations and five supported granularities1/8/32/64/128. Stock88-byte KV stack object, value_len+12 and addr.value+84 independently select short enums against the tested unchanged default-enum candidate92/+16/+88. This does not prove a unique compiler flag or source revision.

Magic offsets4/8/20/40/80 independently select granularity1 in the pinned unchanged header/source family. Counts20/20/20/24/32 alone cannot select1 against8/32. Enum choice does not change these disk offsets; granularity does not change the sampled RAM KV layout. These are two independent candidate constraints, not ten behavioral tests. Init_ok24/lock28/unlock32 match both enum variants, so those fields do not independently discriminate enum width or FAL mode.

Correction: 'nonzero status result suppresses second call' needs low-byte qualification. Stock5445D2 UXTB precedes zero comparison;0x100 takes flash-write path, whereas0x101 returns1 without it. Both final returns narrow to8bits. This is static instruction evidence; no provider runtime fixture was run. Legal enum provider values may fit8bits, but the unchecked raw-word formulation is too broad.

## Alternative configuration limits

Caches64/64 remain a matching candidate, not uniquely recovered. With other unchanged short-enum layout assumptions, db_size=172+8*K+24*S; stride2220 constrains K+3*S=256. For example K76/S60 and K64/S64 give the same stride. Cache-member offsets and loop bounds could discriminate them. Name limits61..64 all align the sampled addr fields to80, so nearby name limits require direct name-limit or copy-loop evidence. File/FAL options, auto-update and TSDB macro state are outside this matrix; unchanged struct/layout assumptions and matching compiler representation remain conditional. Cortex-M4 layout probes with Apple clang and GNU declaration headers do not identify a Cortex-M33 firmware producer or compare instruction bytes.

## Remaining finite source opportunities

1. Execute bounded get_kv and get_blob source comparisons with explicit find/read/lock providers: present/missing keys, requested<equal>recorded lengths, null buffer/output-length pointer, ignored read error, initialized/uninitialized parent and optional lock/unlock order. They would close new finite provider contracts, not flash behavior.
2. Execute write_kv_hdr with status0/1 and raw0x100/0x101, flash-write success/error, verify status arguments6/1/false, shifted address/header+4, count20, narrowing and write suppression. This tests the correction above; mocks must remain explicit.
3. Inspect authenticated cache member offsets/loop bounds and name-length checks to discriminate the remaining configuration equivalence classes. The ten-probe matrix alone cannot close them. No need to repeat constructor or layout cases already sealed.

Full find_kv/status/flash/FAL provider implementations, physical flash delivery, source completeness and byte-identical rebuild are unresolved. Useful static evidence is therefore not exhausted globally, though the ten-probe family has exhausted its stated enum/granularity alternatives.

## Previously completed HCI caller audit

hci-caller-review-2026-10-10 independently replayed both cases exactly with12checks PASS. Normal caller/parser/security dispatch/copy ordering and allocation-failure queue preservation/credit processing are closed under explicit providers. Request token7 is distinct from controller status0. Actual controller/transport ordering, queued-request scheduling and hardware completion remain unresolved; combining synthetic queue and caller fixtures is not live delivery evidence. Report: ../hci-caller-review-2026-10-10/REPORT.md.
