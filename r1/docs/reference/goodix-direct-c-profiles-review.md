# Direct Goodix lifecycle wrappers reconstructed in C

The existing C Goodix policy unit now owns five additional native entries:

| Entry | C symbol | Behavior |
| --- | --- | --- |
| `0x50870` | `r1_goodix_stop_stock_profiles` | Stop modes `0x2000`, then `0x4000`; close bus, release transport and tail-dispatch reset low |
| `0x50892` | `r1_goodix_start_profile_4000` | Power/transport/bus setup, RTOS delay ten, demo init, tail-call configuration-switch start for mode `0x4000`, configuration two |
| `0x508b6` | `r1_goodix_start_profile_2000` | Same sequence for mode `0x2000` |
| `0x508da` | `r1_goodix_identity_probe` | Power and transport setup, Nordic busy delay fifty, open bus, query, save low byte, close bus/transport/reset and return saved byte |
| `0x2e734` | `r1_goodix_sampling_mode_glue` | Communication result zero maps to full-width `-91`; nonzero maps to zero |

REA confirms each actual instruction/call boundary. Ghidra's pseudocode expands
operations beyond the start wrappers' tail target; the C wrappers preserve
the actual `Gh3x2xDemoStartSamplingWithCfgSwitch` boundary at `0x2e61c` rather
than copying that expansion into another implementation. The stop wrapper's
last power call is a required tail call. The two zero-argument start wrappers
use ordinary typed calls to the two-argument SDK entry; their compiled tail
behavior is verified at execution time because Clang's musttail signature
constraints do not permit that argument-count change.

The communication helper's unusual zero/nonzero mapping is retained exactly,
without interpreting it as a conventional success predicate. Identity preserves
only its low byte across cleanup: communication result zero produces `0xa5`,
nonzero produces zero. The SDK communication result is declared with its actual
signed-byte return type; probes additionally exercise raw register stress words,
which are not claims about valid SDK return values.

The probe passes 240 paired stock/C cases (480 executions), covering all five
entries, eight external result words and interrupt-mask combinations. It
compares full external arguments and ordered calls, result truncation/preservation,
original stack/return address at tail boundaries, preserved registers and masks.
The identity tests execute the actual native/C communication glue, including
compiler inlining where selected, with only its external communication provider
modeled. A deliberately inverted condition fails: stock returns identity byte
`0xa5` for communication result zero while the variant returns zero.

Regressions pass for initialization (4,096), acquire (2,080), release (2,080)
and profile switching (192). The normal report
`build/sources-goal-r1-goodix-direct-profiles/report.json` compiles 569 R1 units
without failures or duplicate strong symbols; imports remain 197 application
and 34 bootloader. `make sources-check` passes.
[Machine evidence](goodix-direct-c-profiles-review.json) binds REA, source,
execution probes, negative control and normal build by hash.

Compiled sizes are respectively 34/38/38/48/20 bytes, versus native
34/36/36/42/18 bytes. None of these new bodies is byte-qualified. The canonical
source plan retains the separately qualified bus/sink providers unchanged;
source-built accounting remains 3,761 bytes in the last verified hybrid.
Hardware/SDK/RTOS boundaries are modeled. Private frames, caller-clobbered
registers/flags, concurrency, actual scheduling and physical reset/bus/timing,
complete source-only byte identity and G2 corpus gates remain unverified.
