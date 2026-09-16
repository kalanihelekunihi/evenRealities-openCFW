/* SPDX-License-Identifier: MIT */
/* Recovered diagnostic text; spelling preserved for firmware compatibility. */
#define MESSAGE(name, text) const char denoise_msg_##name[] \
    __attribute__((section(".denoise_msg." #name))) = text
MESSAGE(start, "[LVP_MODE_DENOISE]Init denoise mode\n");
MESSAGE(none, "[LVP_MODE_DENOISE]No noise reduction\n");
MESSAGE(rate, "samplerate %d frame size %d\n");
MESSAGE(drc_ok, "[LVP_MODE_DENOISE]Init DRC\n");
MESSAGE(double, "[LVP_MODE_DENOISE][DOUBLE_MIC_DENOISE]Init gsc Beamforming\n");
MESSAGE(double_fail, "[LVP_MODE_DENOISE]_beamformingInit Failed !!!\n");
MESSAGE(single, "[LVP_MODE_DENOISE][SINGLE_MIC_DENOISE]Init Imcra\n");
MESSAGE(single_fail, "[LVP_MODE_DENOISE]_imarcInit Failed !!!\n");
MESSAGE(drc_fail, "[LVP_MODE_DENOISE]FrameDrcStateInit Fail!\n");
MESSAGE(audio_fail, "[LVP_MODE_DENOISE]LvpAudioInInit Failed !!!\n");
MESSAGE(audio_ok, "[LVP_MODE_DENOISE]LvpAudioInInit OK!!!\n");
MESSAGE(ok, "[LVP_MODE_DENOISE]Denoise Init OK!!!\n");
