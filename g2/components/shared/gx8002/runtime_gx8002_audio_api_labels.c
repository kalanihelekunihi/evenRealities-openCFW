/* SPDX-License-Identifier: MIT */
/* Diagnostic function names retained by the deployed public audio API. */
const char open_cfw_gx8002_audio_labels_config[] __attribute__((section(".rodata.labels_config"),aligned(1))) =
    "gx_audio_out_config_i2s\0gx_audio_out_config_dac";
const char open_cfw_gx8002_audio_labels_drain[] __attribute__((section(".rodata.labels_drain"),aligned(1))) =
    "gx_audio_out_drain_frame";
const char open_cfw_gx8002_audio_labels_controls[] __attribute__((section(".rodata.labels_controls"),aligned(1))) =
    "gx_audio_out_get_db\0gx_audio_out_set_mute\0gx_audio_out_get_mute";
const char open_cfw_gx8002_audio_labels_power[] __attribute__((section(".rodata.labels_power"),aligned(1))) =
    "gx_audio_out_suspend\0gx_audio_out_resume\0gx_audio_out_set_fixed_src\0gx_audio_out_get_sdc_src";
