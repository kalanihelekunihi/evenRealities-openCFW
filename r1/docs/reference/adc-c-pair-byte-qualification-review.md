# ADC pair C provider qualified against stock bytes

The canonical source plan now includes the exact eighteen-byte C body for
`r1_temperature_pair_read` at stock `0x50d2a`. Its historical name remains a
source-mapping label: the routine acquires a raw ADC average, stores it, then
independently acquires/scales another ADC average and stores that second word.
The [behavioral review](adc-c-pair-review.md) covers those ordering obligations.

The official qualifier evaluated three source units under recorded/O2/Os/Oz/Og
options: all fifteen compiled. Only candidate inputs were filtered; official
compilation, named anchors, binding validation, linked equality and selection
logic were unchanged. Oz emits the eighteen-byte pair with direct bindings to
native average `0x50c90` and native scaling `0x50d00`. The complete linked body
matches stock SHA-256 `71a08b9d39573b1e85bccea116a8d174e62b6bcda2c5a87eb503a5056a2a36b9`.
The averaging kernel, frame bridge and tested Goodix policies did not qualify.

There is no overlap with the previous canonical plan. The merged candidate
plan passed a full R1 hybrid build before the exact merged plan was promoted.
The produced 646,408-byte application is byte-for-byte equal to the locked
official application, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The hybrid report binds the promoted plan's hash and marks the new span as
source-built by the expected C provider.

Source-built accounting increases by eighteen C instruction bytes to 3,779
stored bytes: 360 compiled C instruction bytes, 154 source-assembly instruction
bytes and 3,265 compiled non-executable bytes. Resource files supply 248 bytes;
642,381 bytes remain unclassified binary pull-through. The hybrid explicitly
reports source completeness false. Exact output does not establish a complete
source rebuild, and this provider's calls still reach retained native average
and scaling code at their assigned addresses.

[Machine evidence](adc-c-pair-byte-qualification-review.json) binds the scope,
qualifier, selections, canonical plan before/after, C sources, hybrid report,
coverage and generated application. The build is
`build/hybrid-goal-r1-analog-qualification`. Normal composition remains the
separately verified 571 R1 units with 197 application and 34 bootloader imports.
`make sources-check` and diff whitespace checks pass; no firmware C changed
during qualification.

Physical ADC/timing validation, the unqualified C average/scaling implementations,
complete source-only linking/byte coverage and G2 corpus gates remain outstanding.
