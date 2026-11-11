# Bind record reinitialization to the canonical C lifecycle entry

The missing r1_record12_reinitialize symbol is now a C alias of
r1_gomore_force_reinitialize_native in native_health_lifecycle.c. Stock
profile-change 0x6c53c and sensor-failure 0x6c1c0 both transfer to 0x4c37c,
which is already implemented by that canonical function. This closes the
import without another algorithm, wrapper body or state owner. Both symbols
have the same linked entry address. The lifecycle unit's allocated bytes and
relocation records remain identical to the preceding build.

Fresh REA bytes for all three entries match the locked application. REA's
function manager merges the 0x6c53c block into the 0x6c66c dossier, so that
dossier's selected entry/pseudocode is not used as proof of this separate
call site. The instruction bytes and executed stock path establish the tail
target. The companion JSON records the byte receipts and hashes.

Verification executes the stock and normal compiled C canonical force entry,
profile-change caller and failure-counter caller. All 2968 cases pass: eight
force-entry cases, 800 profile cases and 2160 failure cases. They vary ready
and authorization flag bits, inclusive profile-change windows, failure counts
around 59/60 and 255 rollover, status words, logging modes, logging callbacks
that mutate the failure count, and interrupt masks. The actual force body
and source memclr/memset execute. Tests check authorization gating, ordered
noop/clear/init effects, all 736 cleared bytes before initializer entry,
mode 1, final state, logs, saved registers, SP and interrupt masks. C code is
guarded against entering stock instructions.

Authorization dispatch, noop and the deeper lifecycle initializer are modeled
with caller-clobber poisoning and payload mutations. Thus these tests prove
the binding and caller-to-force integration, not full authorization, engine
reinitialization or physical sensor operation. Private frames, incidental
caller-clobbered outputs, faults and concurrency remain excluded. Four
compiled defects are detected: wrong alias target, short clear, wrong
initializer mode and wrong authorization bit. A clean final baseline is
rerun after the controls.

All 786 R1 units compile without failures or duplicate strong symbols.
Application imports fall from 106 to 105, with none added; bootloader linker
metadata imports remain 22 and strict source bootloader linking succeeds.
All 783 unrelated nongenerated object hashes remain unchanged. The two
generated bootloader objects retain allocated bytes and relocations despite
metadata changes. Global source checking retains the unrelated unlisted G2
resident_rom_thumb_set.S failure. Full application linking remains unfinished;
no new source-plan qualification or byte-identity claim is made.
