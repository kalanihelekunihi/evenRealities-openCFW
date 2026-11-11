# R1 optical estimator root in C

`native_gomore_optical_estimate.c` implements stock `0x69834` as the shared
`r1_gomore_optical_estimate_native` provider. It covers gap/reset and warmup
paths, optical peak/control reduction, state smoothing, sparse-history fallback
and rate/confidence selection. The earlier checked utility remains named
`gomore_primitives_optical_period_estimate_checked`; it is not the native ABI provider.

REA pseudocode and complete instruction evidence cover 1,196 bytes in two ranges,
`0x69834..0x69c4f` and `0x69c8a..0x69d19`. The application SHA-256 is
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The [machine receipt](gomore-optical-root-c-review.json) records inputs and hashes.

The candidate preserves the observed 1,328-byte root frame at provider calls.
Its workspace starts at SP+16; expanded samples, controls, minimum/maximum
counts and minima/maxima start at SP+48, +1048, +1208/+1212 and +1216/+1236.
Incoming output pointers are captured before either output store. Private
cache slots and register saves differ from stock and are excluded from equality.
This frame depends on the recorded GCC9 profile and generated object.

There are 148 passing native-dependency replay pairs, 945 modeled-provider
pairs and 64 native/C respiratory-plus-optical caller pairs. Checks compare
full external state, write order, provider arguments and stack depths, R0,
FPSCR, SP and preserved general/FP registers. Models cover output aliasing,
provider clobbers and ignored return statuses, transition/counter boundaries,
confidence and fallback thresholds, signaling NaNs, rounding/flush modes and
old/new smoothed values. Expanded fallback samples are hashed at the provider
boundary. All eight deliberate behavioral defects are rejected.

Actual replay uses the reconstructed optical processing providers; remaining
software math/runtime functions execute stock. Respiratory replay retains its
native helper leaves. These bounded fixtures do not establish exhaustive
behavior, physical sensor performance or a complete source-only firmware link.

The fresh normal build compiles 706 units (632 application, 74 bootloader),
with no failures or duplicate strong symbols. Application imports fall from
179 to 178; bootloader imports remain 34. Qualification selects zero bytes for
this root because its anchored relocation pattern is not exact. The canonical
plan is unchanged: 4,381 source-built executable bytes, 641,779 retained stock
executable bytes and 248 resource bytes. The fresh R1 hybrid remains equal to
stock; that hybrid equality does not establish source completeness or byte
identity for this C candidate.
