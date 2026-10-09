# Configure translation-unit discriminator

`environment.py` extracts the complete Configure definition from each retained
preprocessed translation unit, removes line directives and normalizes whitespace.
All three definitions have SHA-256
`191559a1fa56d41da22145ec4f352c70106b56033f9441d85c4b1e2471077658`.
Normalized definitions are visible alongside `environment-results.json`.

All 27 consumed noncompiler files in each new build match the hashes in the
previous 13.3 reproduction receipt. This covers pinned PDL source/device/IP
headers, CMSIS/core-lib and the system header stub; compiler-owned standard
headers are separately recorded, not claimed identical across versions.
The Configure body itself nevertheless preprocesses identically for the three
older releases. No producing-build preprocessed file exists for comparison.

The function has no external calls. Its explicit indexed loops expand to eight
global-function words and three mode records. Configuration is supplied through
the runtime pointer; no generated cycfg file is consumed. Source inlining of
external providers cannot explain this standalone body's differences because
there are no such calls in the expanded definition. The consumed headers fix
the public register/configuration layouts and volatile declarations for these
builds; exact register effects are already covered by the earlier behavioral
composition, but that does not prove producer layout/source equality.

This rules out differing PDL/include file contents between these recorded
experiments as the immediate explanation for their compiler-dependent output.
It does not rule out another producing PDL revision, a private edit, producer
flags, compile-time declarations, LTO/whole-program context or compiler-specific
lowering. The original flags beyond the matched family remain unknown. No
producer macro set or preprocessed translation unit has been authenticated.

Prior 13.3 loop options `-fno-tree-ch` and `-fno-thread-jumps` retain the exact
same mismatch; `-fno-guess-branch-probability` worsens it. Those experiments
were not repeated. No independently motivated new flag follows from the
identical expanded definitions, so no arbitrary flag sweep, patched loop,
manual scheduling or byte fitting was performed.

The next source-led input is a genuinely different authenticated Configure
revision or the original translation-unit/build configuration. A bounded
upstream history comparison should identify actual loop/declaration changes
before compiling any revision. The existing pinned source is already covered;
reacquiring or rebuilding it with identical settings adds no evidence.

## Focused used-type comparison including 13.3

The authenticated native 13.3 compiler was used only to preprocess the same
source/includes; no duplicate object comparison was run. Its argv, exit code,
compiler and preprocessed-output hashes are in `13.3-preprocess-receipt.json`.
`types.py` compares expanded definitions for uint32_t, MSCLP block/mode types,
status/key enums and configuration/context structures. All recovered definitions
are identical across 10.3, 11.3, 12.2 and 13.3. Volatile counts and type
attributes are recorded in `type-comparison.json`; readable definitions are in
`Configure-used-types.json`. No active packing/alignment or non-diagnostic
pragma appears in these translation units. Diagnostic suppression pragmas do
not establish a code-generation difference.

This removes an observed qualifier/packing/declaration discrepancy as a reason
for another experiment. It is not a compiler sizeof/offsetof probe or proof of
producer headers. No further compilation is motivated by these results.
