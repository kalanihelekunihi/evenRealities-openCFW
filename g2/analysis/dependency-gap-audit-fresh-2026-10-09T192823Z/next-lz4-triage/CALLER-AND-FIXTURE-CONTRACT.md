# Locked LZ4 caller/API and finite fixture review

Independent static review: eleven baseline checks PASS in CALLER-CONTRACT-BASELINE.json. Three decoder ranges, five called helper ranges and every serialized listing byte match locked main SHA19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701. Thumb BL immediate decoding independently confirms the safe wrapper branch and enumerates direct-call encoding candidates. No execution or builds performed. Capstone is unavailable in host Python; this audit authenticated owner listing bytes and reviewed narrow Thumb encodings rather than installing another tool.

## API and distinct extents

Safe wrapper54F338–54F356: r0=source, r1=destination, r2=signed compressedSize, r3=signed maxDecompressedSize. It keeps these registers, writes five stack arguments [0,0,destination,0,0] and BLs54EF08. Compared to authentic source signature, these are decode_full_block, noDict, lowPrefix=destination, dictStart=NULL, dictSize=0. Prologue push{r3,r4,lr} plus20byte subtraction makes the call stack32bytes below entry, preserving8byte alignment. It returns generic result directly. No independent fast decoder is present in these three selected extents; generic optimized/wild-copy paths are internal safe API implementation, not the unsafe LZ4_decompress_fast API.

Generic54EF08–54F338: saves r0 and registers then40bytes locals, accesses incoming stack arguments at offsets80,84,88,92,96. Its immediate entry rejects null source or negative output capacity with-1. At zero output capacity and full decoding it returns0 only for compressedSize1 and source token0; otherwise-1. At nonzero output capacity compressedSize0 returns-1. Partial flag exists in the generic body but the selected safe wrapper fixes it to0. Error path54F0B0–54F0B8 forms complement(ip-src), i.e. -(consumed input)-1; success54F0C2–54F0CA returns output pointer minus destination. Keep signed32 return interpretation and consumed-position-sensitive errors separate from output equality.

read_variable_length54EE90–54EF06 is an internal length helper, not another public decompression API. It loads an error sentinel via authenticated literal references on its input-bound/overflow paths. All five further helper extents must execute from locked bytes:439710 (overlap-aware copy),439BE4 (copy),54EE3E/54EE4E/54EE6E (local copy helpers). Literal/tables referenced outside function envelopes must remain mapped and hash-bound; function text alone is not sufficient dependency closure. Exact instruction semantics beyond the narrow reviewed contract remain owner execution evidence.

## Actual locked direct caller; navigation still unbound

The raw halfword BL scan finds one direct encoding to safe54F338 outside its implementation:4E0C28. Narrow contiguous body4E0C0C–4E0C34 is:

- push{r4,lr}; r4=r2;
- require nonzero r0, r4, r1 and r3, otherwise return0;
- r2=r1; r1=r4; BL54F338;
- signed compare result with1; if less, result=0; pop{r4,pc}.

Thus this caller's arguments are (source, compressedSize, destination, capacity). It conflates negative errors and zero-byte success into0, retaining only positive lengths. Exact body bytes:10b51400002805d0002c03d0002901d0002b01d1002006e00a0021006ef086fb012800da002010bd. The historical symbol TSV omits this body; its extent here comes from explicit narrow push/return decoding, not a newly admitted canonical symbol. A raw encoding scan cannot exclude indirect/tail callers or data coincidences.

No authenticated navigation root/argument producer into this wrapper has been established by this audit. Emulator56192e mismatches locked bytes and remains unusable for that attribution. Direct safe API experiments can proceed without claiming navigation binding. A navigation-level contract needs a hash-bound locked caller/root feeding4E0C0C (or another verified safe call), its size/buffer fields and actual state constraints. No hardware/private source is inherently needed for that static binding, but it is missing now.

## Twelve-fixture contract corrections

Keep the finite proposed12 categories; instantiate concrete bytes/capacities and freeze before execution. Empty input versus encoded token00 must include explicit output capacities: empty compressed input returns-1, while encoded00 at capacity0 is special successful0. Avoid null pointers/negative sizes except separately declared directed API fixtures; they are not malformed raw blocks.

Literal extension/payload and match offset/extension truncations are useful only if they reach the intended source guard, rather than an earlier last-literal restriction. Derive cases from both actual pinned source branches and record expected guard/consumed-position. Preserve exact negative return values rather than classifying all as generic errors.

Zero offset is an essential hypothesis, but do NOT assume rejection: the upstream implementation includes offset0 initialization to silence memory-sanitizer warnings. Host Python rejects zero offset; this is not an independent stock oracle. Likewise Python accepts some raw blocks that violate upstream last-literals restrictions. Source outcomes, not the host permissive/strict policy, must define the comparator.

Valid overlapping-match fixture must retain at least five final literal bytes and a last-match start at least twelve decoded bytes before block end, with lengths/capacity chosen to reach the intended copy branch. An invalid final-match fixture can explicitly test those constraints, but label it invalid by the authentic format/parser rules. Truncated-match fixtures need enough available output/input room to reach the selected branch.

Memory oracle: immutable full source and canaries/unmapped memory beyond declared input/destination capacities; record every write/read range if engine supports it. Require untouched destination bytes beyond capacity. LZ4 wild-copy can write beyond final returned logical length while remaining inside capacity: do not require the entire in-capacity output tail to stay sentinel as a public API guarantee. Compare source/stock full write footprints as evidence, while only decoded prefix and contract-required guards are correctness assertions. On error, destination contents/partial writes are not guaranteed unchanged; report them independently. Decoder reads are bounded by API input size; extra readable backing memory must not silently conceal out-of-input reads.

No fixture execution reviewed yet. Direct stock/public1.9.4/public1.10.0 behavior remains separate from byte identity, exact producer, physical GPU/navigation behavior and whole firmware coverage. Stop after the frozen12cases plus local branch/error review; do not broad-sweep flags or import old profile addresses.
