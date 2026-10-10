# G2 current-corpus tool shortcut evaluation — 2026-10-10

## Scope and gates

This is a bounded read-only evaluation of Ghidra-MCP, Ablation, and REA against
an already authenticated ARM/Thumb corpus slice retained by the fourth shortcut
frontier.  It does not admit evidence into the canonical P2 ledger, change an
analysis processor, alter a submodule pin, reconstruct firmware, or open G2–G6.
`g2/workflow/state.json` remained `P2_EXECUTING` throughout.

The selected target is the existing analysis-only ELF for the authenticated
402-byte `SmpHandler` body at `0x537d0c..0x537e9e`:

* ELF SHA-256: `1facc82af2b53a328fdcb3726ef0d4fb3b370fc8ddc808e57c95180c8d9d6cc5`
* original body SHA-256: `c6c182f8937a91efc42995289820d0589b5ae839960cde0d83aec3f40ba0dbba`
* source OTA SHA-256: `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`

The ELF is analysis metadata around original bytes, not producer provenance or
a replacement firmware image. Its explicit Thumb state is independently bound
by the prior receipt and is a prerequisite for this experiment.

## Tool identities

The repository pins were re-read without moving them:

* Ghidra-MCP `9cc29c0f1efb6c63a7d6898c9a23aff39397f992`
* Ablation `97e051b44d1ac8129b35556fe533e6e8b5338db2`
* REA `7aa4d768eb15317a63a476431ed75bafec086033`

REA selected its Ghidra 12.1.4 provider with ephemeral immutable import. The
analysis profile digest was
`d6dcc035b9648ba2aa59ab7f114beeb9f76c9c94e5566de048b8c0495492de26`.

## Results

### Ablation: concrete bounded shortcut retained

The current pin replayed the body as a 402-byte function and enumerated all 24
direct `BL` sites and targets. This agrees with the independently retained GNU
and prior REA instruction validation. For this evidence class, Ablation remains
a useful batch shortcut for direct-call inventory after a reviewer supplies the
correct range and Thumb state.

It also reported four printable byte runs as strings. They are instruction-byte
coincidences and demonstrate why its string output is not admissible without
literal/reference proof. The useful output is therefore direct-call enumeration,
not string recovery, automatic boundary discovery, or semantics.

### REA: useful review transport, incomplete call graph on the bounded view

REA opened the exact ELF by SHA-256 and reported one procedure at `0x537d0c`,
one 402-byte `.text` segment, and an ARM target. Its assembly covered the full
bounded function and its pseudocode exposed the major message-type branches,
four repeated diagnostic arms, queue-drain loop, and normal dispatch arm. This
is concrete review acceleration: a reviewer can request assembly, pseudocode,
bytes, and references through a stable ephemeral session without creating or
mutating a shared Ghidra project.

However, `procedure_callees(0x537d0c)` returned an empty list even though the
same REA assembly contains 24 direct `BL` instructions and Ablation enumerated
all 24 destinations. The analysis-only ELF deliberately maps only the function
body, so its external targets are unresolved. REA's call graph is not a complete
direct-call oracle for bounded single-body views unless reviewed external stubs
or a wider authenticated mapping are supplied. Adding such mappings would be a
new evidence/view construction task and was outside this read-only pass.

REA evidence identifiers from this run:

* overview: `ev_9cb854b33b8e9eb4c0dc2d64b77d4b55e2887062c53391983fbca53fe092905f`
* procedure inventory: `ev_d72e925fa3b1260d4937b62b97782f51f6bcd81716d08cc10252e37240cd8fed`
* assembly: `ev_5137d016dde1ff769192cb2745223d651037ba0fbd426ba4f57ff2e266842a4b`
* empty callee result: `ev_716324ce0b7d34c5c060f344ae6f9315a90c90716063599326ff409d0c95f0c3`
* pseudocode: `ev_c2381811f08652c92ff0600229d76e75e2ed9253dd67254adf94c042d3680c12`

### Ghidra-MCP: no independent current shortcut result

`list_instances` returned no running Ghidra instances. No private or shared
project was opened through Ghidra-MCP, and no firmware program was imported or
mutated. Starting another bridge/project would duplicate the Ghidra 12.1.4
analysis already exercised through REA and would not add an independent oracle.
The prior C-SKY `movih` lift defect and architecture limitations therefore still
bound its semantic value. Ghidra-MCP remains useful for interactive queries only
after a reviewed private project and correct processor/mapping are available.

## Net shortcut decision

There is no new provider identity, source attribution, accepted pseudocode, or
gate advancement from these tools on the current corpus. There is a concrete
workflow improvement with a strict boundary:

1. use Ablation, with authenticated bytes plus explicit reviewed ISA/range
   metadata, for fast direct-call inventory;
2. use REA's ephemeral Ghidra session for assembly/pseudocode review and query
   orchestration;
3. compare REA graph results to the direct instruction inventory and retain
   unresolved external calls explicitly;
4. use Ghidra-MCP only when a reviewed private persistent project adds stateful
   queries that REA's ephemeral session cannot provide.

This does not reopen the fourth frontier's source/dependency exhaustion result.
Further semantic progress still requires canonical P2 review, wider authenticated
load mappings, a corrected and independently reviewed architecture lift, or a
genuinely new authenticated producer input.

## Reproduction

From the repository root, the Ablation replay is read-only:

```sh
PYTHONPATH="$PWD/third-party/tools/ablation" \
  /Users/kalani/Repos/ablation/.venv/bin/python - <<'PY'
from ablation.analyzers.binary_context import BinaryContext
from ablation.analyzers.func_profiler import FuncProfiler
p = 'g2/analysis/source-discovery-parallel-2026-10-09/ablation-smp-20261010/smp-analysis-only.elf'
ctx = BinaryContext.build(p)
ctx.thumb_funcs.add(0x537d0c)
print(FuncProfiler.from_context(ctx).profile(0x537d0c, end_va=0x537e9e).fmt())
PY
```

Observed header: `402B  24 calls  4 strings`. Validate the 24 calls against
`../source-discovery-parallel-2026-10-09/ablation-smp-20261010/call-validation.json`;
do not promote the four strings.

For REA, open the absolute ELF path with provider `auto`, then run
`binary_overview`, `list_procedures`, `procedure_assembly`,
`procedure_pseudo_code`, and `procedure_callees` for `0x537d0c`. Confirm the
subject hash and analysis-profile digest above before comparing results.

For Ghidra-MCP, `list_instances` reproduced `instances: []`; this is an
availability observation, not evidence about the firmware.
