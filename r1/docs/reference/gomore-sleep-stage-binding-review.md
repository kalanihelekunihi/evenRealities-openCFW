# R1 GoMore sleep stage model binding

`r1/src/application/runtime/native_gomore_sleep_stage_adapter.c` binds the
firmware ABI at stock `0x60dc4` to the existing typed C
`gomore_primitives_sleep_stage_stream_update` owner. It supplies the live
timestamp, peak and activity records, status/output pointers, the 11-byte
mode table, a source-owned tensor-pool constructor and the typed classifier.
The adapter consumes the seven native ABI arguments; stock does not use its
second elapsed argument within this stage.

The two classifier model views are in
`r1/src/application/runtime/native_gomore_sleep_stage_model.inc`. Their 51
descriptors per model are derived from the source-owned descriptor tables at
stock `0xB1C4C` and `0xB2048`. Each table describes seven convolution blocks
and eight affine weight/bias pairs. Descriptor addresses and element counts
form a gap-free span of 21,824 bytes per model. Both source-owned spans were
compared byte for byte with the locked application: the SHA-256 values are
`da353b02976da84378f6321b2f5ec7cbc4c184eb706b1d6a7fad5499258c4861`
and
`09f807f0c73daae139a0f2aa39ec37b4c57db8c6a7178e943aec6bd8913ee82c`.
The C views point into `r1_model_data_words`; they do not duplicate model
parameters or retain executable firmware bytes.

The ignored host probe
`build/r1-gomore-sleep-model-binding-20261111/probe.c` compiles the real
GoMore primitive, tensor runtime and model words. Both modes execute the
complete typed classifier on a 90-sample input, return a stage in 0..3 and
produce finite scores. The probe verifies the model views are usable by that
implementation. It is not a stock/C classification comparison, a complete
streaming-stage replay or a physical sleep-stage validation. The adapter
returns `UINT32_MAX` if the typed primitive rejects its inputs; the stock
function's normal path returns zero. Invalid-input equivalence remains open.

`build/sources-r1-gomore-sleep-stage-binding-v2-20261111/report.json` compiles
945/945 application and 82/82 bootloader units without failures or duplicate
strong symbols. The strict bootloader link is valid. The strict application
receipt `build/r1-link-gomore-sleep-stage-binding-v2-20261111/report.json`
has eight undefined functions, uses 658,728 of 696,320 flash bytes and has
no overflow. Its `.bss` ends at `0x20036760`, below the `0x20040000` RAM
limit. This closes the stage import but does not complete the application.
