/* Typed views over the verified, source-owned non-executable model words. */
/* Descriptor tables: stock 0xB1C4C and 0xB2048; data: 0xB2458 and 0xB7998. */
static const gomore_primitives_sleep_stage_classifier_model sleep_models[2] = {
    {
.convolution = {
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2458)), .weight_count=12u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2470)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2478)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2480)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2488)), .parameter_count=4u },
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2490)), .weight_count=96u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2550)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2560)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2570)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2580)), .parameter_count=8u },
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2590)), .weight_count=192u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2710)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2720)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2730)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2740)), .parameter_count=8u },
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2750)), .weight_count=192u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B28D0)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B28E0)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B28F0)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2900)), .parameter_count=8u },
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2910)), .weight_count=192u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2A90)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2AA0)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2AB0)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2AC0)), .parameter_count=8u },
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2AD0)), .weight_count=192u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2C50)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2C60)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2C70)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2C80)), .parameter_count=8u },
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2C90)), .weight_count=192u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2E10)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2E20)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2E30)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B2E40)), .parameter_count=8u },
},
.projection = {
    { .weights=MODEL_PTR(int8_t, UINT32_C(0x000B2E50)), .weight_count=3840u, .rows=32u, .columns=120u, .weight_scale=0x1.b36ca80000000p-9f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000B3D50)), .bias_count=32u },
    { .weights=MODEL_PTR(int8_t, UINT32_C(0x000B3D90)), .weight_count=1024u, .rows=32u, .columns=32u, .weight_scale=0x1.0d1ad00000000p-8f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000B4190)), .bias_count=32u },
},
.recurrent = {
    { .input = { .weights=MODEL_PTR(int8_t, UINT32_C(0x000B41D0)), .weight_count=3072u, .rows=96u, .columns=32u, .weight_scale=0x1.34efbe0000000p-8f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000B71D0)), .bias_count=96u }, .recurrent = { .weights=MODEL_PTR(int8_t, UINT32_C(0x000B4DD0)), .weight_count=3072u, .rows=96u, .columns=32u, .weight_scale=0x1.b149220000000p-8f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000B7290)), .bias_count=96u } },
    { .input = { .weights=MODEL_PTR(int8_t, UINT32_C(0x000B59D0)), .weight_count=3072u, .rows=96u, .columns=32u, .weight_scale=0x1.81326c0000000p-8f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000B7350)), .bias_count=96u }, .recurrent = { .weights=MODEL_PTR(int8_t, UINT32_C(0x000B65D0)), .weight_count=3072u, .rows=96u, .columns=32u, .weight_scale=0x1.02c4800000000p-7f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000B7410)), .bias_count=96u } },
},
.post_recurrent = { .weights=MODEL_PTR(int8_t, UINT32_C(0x000B74D0)), .weight_count=1024u, .rows=32u, .columns=32u, .weight_scale=0x1.2a28660000000p-8f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000B78D0)), .bias_count=32u },
.output = { .weights=MODEL_PTR(int8_t, UINT32_C(0x000B7910)), .weight_count=128u, .rows=4u, .columns=32u, .weight_scale=0x1.8b43320000000p-8f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000B7990)), .bias_count=4u }
},
    {
.convolution = {
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7998)), .weight_count=12u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B79B0)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B79B8)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B79C0)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B79C8)), .parameter_count=4u },
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B79D0)), .weight_count=96u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7A90)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7AA0)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7AB0)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7AC0)), .parameter_count=8u },
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7AD0)), .weight_count=192u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7C50)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7C60)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7C70)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7C80)), .parameter_count=8u },
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7C90)), .weight_count=192u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7E10)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7E20)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7E30)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7E40)), .parameter_count=8u },
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7E50)), .weight_count=192u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7FD0)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7FE0)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B7FF0)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B8000)), .parameter_count=8u },
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B8010)), .weight_count=192u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B8190)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B81A0)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B81B0)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B81C0)), .parameter_count=8u },
    { .weights_half=MODEL_PTR(uint16_t, UINT32_C(0x000B81D0)), .weight_count=192u, .scale_half=MODEL_PTR(uint16_t, UINT32_C(0x000B8350)), .offset_half=MODEL_PTR(uint16_t, UINT32_C(0x000B8360)), .variance_half=MODEL_PTR(uint16_t, UINT32_C(0x000B8370)), .mean_half=MODEL_PTR(uint16_t, UINT32_C(0x000B8380)), .parameter_count=8u },
},
.projection = {
    { .weights=MODEL_PTR(int8_t, UINT32_C(0x000B8390)), .weight_count=3840u, .rows=32u, .columns=120u, .weight_scale=0x1.d943c60000000p-9f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000B9290)), .bias_count=32u },
    { .weights=MODEL_PTR(int8_t, UINT32_C(0x000B92D0)), .weight_count=1024u, .rows=32u, .columns=32u, .weight_scale=0x1.3557400000000p-8f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000B96D0)), .bias_count=32u },
},
.recurrent = {
    { .input = { .weights=MODEL_PTR(int8_t, UINT32_C(0x000B9710)), .weight_count=3072u, .rows=96u, .columns=32u, .weight_scale=0x1.4926680000000p-8f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000BC710)), .bias_count=96u }, .recurrent = { .weights=MODEL_PTR(int8_t, UINT32_C(0x000BA310)), .weight_count=3072u, .rows=96u, .columns=32u, .weight_scale=0x1.c6198a0000000p-8f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000BC7D0)), .bias_count=96u } },
    { .input = { .weights=MODEL_PTR(int8_t, UINT32_C(0x000BAF10)), .weight_count=3072u, .rows=96u, .columns=32u, .weight_scale=0x1.5a9f2e0000000p-8f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000BC890)), .bias_count=96u }, .recurrent = { .weights=MODEL_PTR(int8_t, UINT32_C(0x000BBB10)), .weight_count=3072u, .rows=96u, .columns=32u, .weight_scale=0x1.5f22fc0000000p-7f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000BC950)), .bias_count=96u } },
},
.post_recurrent = { .weights=MODEL_PTR(int8_t, UINT32_C(0x000BCA10)), .weight_count=1024u, .rows=32u, .columns=32u, .weight_scale=0x1.c3a5a40000000p-9f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000BCE10)), .bias_count=32u },
.output = { .weights=MODEL_PTR(int8_t, UINT32_C(0x000BCE50)), .weight_count=128u, .rows=4u, .columns=32u, .weight_scale=0x1.60c6a20000000p-8f, .bias_half=MODEL_PTR(int16_t, UINT32_C(0x000BCED0)), .bias_count=4u }
},
};
