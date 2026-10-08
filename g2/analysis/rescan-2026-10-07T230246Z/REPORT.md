# OpenCFW change scan — 2026-10-07 23:02 UTC

Read-only inspection of existing source and receipts. Only this new report and snapshot were written. No builds, emulator runs, staging, shared-state changes or firmware changes. Concurrent work may advance after this snapshot.

Compared with the22:16 source scan: 421 → 433 bootloader/foundation C, header and assembly files; 12 added, 0 modified, 0 removed. File counts include reused variants and are not reconstructed-function counts.

Added files:

- `g2/components/bootloader/initializer_callbacks/pcm22_deferred21_native/initialized_data.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_deferred21_native/interfaces.h`
- `g2/components/bootloader/initializer_callbacks/pcm22_deferred21_native/pcm22_deferred21.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_deferred21_native/pcm22_sequence22.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_deferred21_native/runtime_transition.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_deferred21_native/runtime_transition.h`
- `g2/components/bootloader/initializer_callbacks/pcm22_deferred21_native/startup_events_a.h`
- `g2/components/bootloader/initializer_callbacks/pcm22_deferred21_native/startup_runtime.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector23_native/initialized_data.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector23_native/interfaces.h`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector23_native/pcm22_sequence23.c`
- `g2/components/bootloader/initializer_callbacks/pcm22_selector23_native/startup_events_a.h`

## Existing checkpoint evidence

| Checkpoint | ELF hash prefix | Identity-bound passing integration cases | Actual ELF hash matches | Final report present |
| --- | --- | --- | --- | --- |
| pcm22-deferred21-rollback-integrated | e5c70f86f097 | 7/7 | True | True |
| pcm22-selector23-integrated | 8aca98ea3043 | 7/7 | True | True |
| pcm22-selector10-integrated | 20d00c40d1d9 | 7/7 | True | False |

The previously pending deferred/rollback checkpoint now has all seven integration cases passing. Selector23 additionally has a delivered component directory. Selector10 is independently compiled and bound in the224-object candidate:241 direct comparisons cover its entire218-byte original body at0x428d90..0x428e6a; two native16→12 chain fixtures pass without redirecting its table entry to selector23. Five unsupported selectors remain:4,7,9,13,19. Selector10 has no final REPORT.md or canonical component delivery at scan time, so integration PASS is not treated as completion of every reproduction/validation obligation. Regression job counts and return codes are recorded in snapshot.json; existing receipts were inspected, not rerun.

## Coverage and scope

Against the frozen component audit, 110 selected input hashes were checked; 0 have changed. Changed paths are listed in snapshot.json. This check is not a fresh exhaustive coverage calculation: the audit's frozen measurements remain its own historical snapshot. The added selector10 body extends the audit's nine explicitly mapped PCM C bodies from2656 to2874 original bytes (+218), a bounded lower-bound increase; this does not establish source replacement across the bootloader or entire OTA. The production bundle still depends on official payload providers; zero complete source-built payloads or byte-identical source-built bundles are demonstrated by these new receipts.

None of the newly added canonical sources is ignored: 0 ignored of12 checked. Candidate ELF visibility rule: `.gitignore:15:build/	g2/build/bootloader-completion/pcm22-selector10-integrated/20d00c40d1d91635249de3a50e15327156e4ee7283dc9fd62aeae40da9628efc/candidate.elf`. A tracked-only view may omit untracked source; build artifacts remain ignored. This scan leaves prior sealed audit and candidate artifacts untouched.

Remaining limits: synthetic MMIO, ROM-call stubs and bounded scheduling fixtures do not establish physical device behavior. The three-slot offline candidates are not deployable firmware. Code-only percentages, exact whole-image source-replacement percentage and residual opaque executable percentage remain unmeasured; compared instruction coverage must not be substituted for them.
