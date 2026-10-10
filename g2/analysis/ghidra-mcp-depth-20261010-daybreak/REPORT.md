# Ghidra-MCP bounded semantic-depth experiment — 2026-10-10

## Scope and preservation

This lane tested Ghidra-MCP itself against one already authenticated ARM/Thumb
analysis view. It used a locally built, private headless Ghidra-MCP 7.0.0
process and its disposable in-memory import. It did not write a Ghidra project,
save the imported program, change an installed processor, edit firmware source,
change a submodule pin, or touch the canonical campaign ledgers.

The target was the retained analysis-only ELF for the 402-byte `SmpHandler`
body at `0x00537d0c..0x00537e9d`:

* ELF SHA-256: `1facc82af2b53a328fdcb3726ef0d4fb3b370fc8ddc808e57c95180c8d9d6cc5`
* authenticated body SHA-256 from the parent receipt:
  `c6c182f8937a91efc42995289820d0589b5ae839960cde0d83aec3f40ba0dbba`
* source OTA SHA-256 from the parent receipt:
  `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`

This is an analysis wrapper around authenticated bytes, not producer
provenance or a replacement firmware image. The explicit Thumb state comes
from the retained parent receipt.

## Tool identity

* Ghidra: Homebrew `12.1.4`
* Java: Homebrew OpenJDK `21.0.12.1`
* Ghidra-MCP gitlink: `9cc29c0f1efb6c63a7d6898c9a23aff39397f992`
* locally built server JAR SHA-256:
  `0209de1a7d58138a87dd61f9c9725832c104d57a1f27defd3b24fbb4368729bc`
* server-reported version: `7.0.0`, headless, 190 endpoints

The build used the pinned submodule and Ghidra's installed jars. Build outputs
are ignored submodule-local artifacts; the extension was not deployed.

## Concrete added leverage

### High P-code recovers useful facts despite a bad stored body extent

The ELF imports one named function at `0x00537d0c`, but its stored Ghidra body
is degenerate: the function service reports size 1 and
`body_end == body_start`. Consequently:

* `disassemble_function` returns no instructions and explicitly warns that the
  stored extent is unreliable;
* `analyze_control_flow` reports zero blocks/instructions and a misleading
  cyclomatic complexity of 2;
* function callees, the function call graph, and xrefs from six sampled `BL`
  sites are empty;
* `analyze_dataflow` fails at the entry with `No PCode operations`.

In the same private program, `get_function_pcode(..., granularity=high)` walks
the decompiler's recovered `HighFunction` and returns:

* 31 basic blocks spanning `0x00537d0c..0x00537e9c`;
* 355 high P-code operations;
* exactly 24 `CALL` operations, agreeing with the prior GNU, Ablation, and REA
  instruction inventories;
* 21 conditional branches, 3 unconditional branches, 19 loads, and one return.

This is a concrete Ghidra-MCP shortcut: query high P-code when a bounded
analysis wrapper has a reviewed entry and ISA state but its stored Ghidra body
or external mapping is incomplete. Never use the ordinary control-flow,
call-graph, xref, or function-size results as the denominator in that state.

### Direct-call argument facts

The high P-code supplies call-site argument count and varnode storage that the
prior direct-call inventory did not preserve. Examples include:

| Site | Target | Observed explicit arguments |
| --- | --- | --- |
| `0x00537d1e` | `0x00542960` | 0 |
| `0x00537d34` | `0x005304d4` | 1, value in `r0` |
| `0x00537d3c` | `0x005375fc` | 1 byte value |
| `0x00537d76` | `0x0044b610` | pointer/global, `0x00537eb4`, `3` |
| `0x00537da2` | `0x0043d574` | 8 arguments; leading discriminator `1` |
| `0x00537de2` | `0x0043d574` | same layout; leading discriminator `2` |
| `0x00537e22` | `0x0043d574` | same layout; leading discriminator `3` |
| `0x00537e54` | `0x0043d574` | same layout; leading discriminator `4` |
| `0x00537e7a` | `0x0052a63c` | 4 arguments |
| `0x00537e82` | `0x004bf9ec` | 2 arguments: global plus stack address |
| `0x00537e94` | `0x0056ee62` | 2 arguments in `r0`, `r1` |

Across all 24 sites, the full ordered summary is in `evidence.json`. These are
decompiler/P-code observations for review, not accepted source signatures. A
wider authenticated mapping is still required to type the external targets.

### Provisional entry ABI and record accesses

The database signature remains `undefined SmpHandler_analysis_label(void)` and
the database parameter list is empty. The decompiler independently recovers two
incoming values:

* an unused 32-bit value in `r0`;
* a pointer in `r1`, tested for null and read at byte offsets `0`, `2`, and `3`,
  plus a 32-bit value at offset `8`.

The recovered control flow compares the byte at offset 2 with `0x20`, `0x1c`,
and `0x0b`; the offset-8 value is dereferenced only on the `0x1c` path. This is
a useful structure-layout and signature candidate for canonical review. It is
not safe to apply automatically because the persistent function prototype,
stored body, and external callee types are unresolved.

## Negative results and boundary

Ghidra-MCP did not add a provider identity, source attribution, accepted
pseudocode, or gate advancement. It did not repair external call xrefs from the
single-body ELF. Its documentation completeness classifier labeled this
nontrivial function a `stub` and scored it from the degenerate body metadata;
that classification is unsuitable for P2 coverage.

No further tool-specific leverage remains on this view without changing the
evidence model. The next useful experiment would need one of:

1. a reviewed wider authenticated address mapping with external call targets;
2. an independently derived correct function body committed only to a private
   scratch project, followed by comparison of ordinary CFG/xrefs to high P-code;
3. reviewed types for the `r1` record and mapped callees, applied in a private
   project to test decompiler stability;
4. a new authenticated ARM, ARC, or C-SKY input whose processor and load map are
   already admitted for P2 review.

The current result is therefore a workflow shortcut, not a new semantic oracle:
use high P-code to extract review candidates from a known bounded body, then
validate every candidate against instructions and canonical P2 evidence. Keep
G2/G3 closed.

## Reproduction

Build the pinned server without deploying it:

```sh
cd third-party/tools/ghidra-mcp
JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home \
PATH=/opt/homebrew/opt/openjdk@21/bin:$PATH \
./gradlew buildExtension \
  -PGHIDRA_INSTALL_DIR=/opt/homebrew/Cellar/ghidra/12.1.4/libexec
```

Start `com.xebyte.headless.GhidraMCPHeadlessServer` using the built JAR plus all
Ghidra Framework, Features, and Processors jars, with `--file` set to:

```text
g2/analysis/source-discovery-parallel-2026-10-09/ablation-smp-20261010/smp-analysis-only.elf
```

Leave `GHIDRA_MCP_ALLOW_SCRIPTS` unset. Optionally restrict paths with
`GHIDRA_MCP_FILE_ROOT` set to the repository root. Connect through the server's
private UDS and run:

```text
list_open_programs
get_metadata
get_functions(function=0x537d0c,
  fields=entry_point,signature,parameters,locals,callees,callers,decompiled_code)
get_function_pcode(function=0x537d0c, granularity=high)
disassemble_function(address=0x537d0c)
analyze_control_flow(function_name=SmpHandler_analysis_label)
get_function_call_graph(function=0x537d0c, depth=1, direction=both)
get_xrefs_from(address=<sample BL site>)
analyze_dataflow(address=0x537d0c, variable=param_2,
  direction=forward, max_steps=200)
```

Confirm the ELF and server JAR hashes above. The expected discriminator is the
contradiction between the degenerate stored-body services and the 31-block,
24-call high-P-code result.

