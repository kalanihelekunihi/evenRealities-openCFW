# G2 FreeType TrueType driver source admission

The authenticated `tt_driver_class` at `0x006DED34` selects the largest
non-CFF outline driver linked by the G2 FreeType configuration. Its complete
non-null class surface is 13 callbacks and 1,188 code bytes. Every callback is
bound to the corresponding FreeType 2.9.1 `ttdriver.c` or `ttobjs.c`
definition under the FreeType Project License.

`analyze_truetype_candidate.py` verifies the official image and class-record
hashes, the 24-word driver ABI, all callable and null class slots, exact body
span hashes and instruction prefixes, upstream source hashes and declaration
order, plus distinctive decompiler shapes for the four larger callbacks that
the stock corpus recovered as standalone functions.

The admitted callbacks are the driver constructor/destructor and interface
lookup; face, size, and slot lifecycle; glyph loading; kerning and advance
queries; and size request/select. This closes the class ABI surface, not every
private helper reachable below it.

The direct private closure admits another 74 private helpers and 21,900 bytes.
It
includes `TT_Load_Glyph`, horizontal/vertical metrics, glyph-loading callback
installation and loader teardown, GX named-instance/MVAR item-store lifecycle,
trick-font recognition and checksum handling, interpreter/zone teardown, size
reset/bytecode teardown, and the complete `loca`/CVT/program/`hdmx` face-table
lifecycle reached by the class callbacks. Direct call edges are checked in
decompiler output where available; the standalone-corpus gaps for
`tt_get_advances`, `tt_glyph_load`, and `tt_size_done` are checked by decoding
their exact Thumb BL targets from authenticated callback bodies.

The indirect closure adds 161 interpreter functions and 15,740 bytes. This is
126 source-ordered opcode-engine bodies (119 targets called by the main
`TT_RunIns` switch, six transitive handler helpers, and `TT_RunIns` itself),
nine arithmetic/state support bodies, and 26 bodies entered through typed
`TT_ExecContext` callbacks. The analyzer checks 27 exact Thumb callback
pointers including the face-interpreter fallback, plus the complete 256-byte
opcode-length and pop/push tables. The resulting attributable driver graph is
248 functions and 38,828 bytes.

Both the direct and indirect dispatch frontiers are empty under a fail-closed
policy: the internal `FT_DEBUG_HOOK_TRUETYPE` remains null because the isolated
candidate exposes no setter, so `TT_Run_Context` deterministically selects the
authenticated `TT_RunIns` fallback. A future debug hook must be admitted as a
new typed policy provider rather than accepted as an unclassified target.

Raw Thumb decoding also corrects a false boundary from the
previous frontier: `tt_loader_done` starts at `0x005F0FB4`; `0x005F0FAC` is
literal/data tail and is not admitted as code.

The isolated `runtime_freetype_truetype_candidate` adapter exposes only the
public `FT_Property_Set`/`FT_Property_Get` boundary for interpreter versions 35
and 40. It neither exposes private `TT_DriverRec` layout nor copies driver
logic. Host qualification checks the stock-proven default v40, switching to
v35 and back, and fail-closed rejection of unsupported v38. The adapter and
upstream source compile into the zero-unresolved Cortex-M55 link harness.

Remaining work is external G2 font payload identity, production linker/section
placement, and stack/WCET qualification. A non-null TrueType debug hook is
deliberately unsupported until its provider is separately authenticated.
