/* SPDX-License-Identifier: MIT */
/* Recovered LvpAudioInSuspend and LvpAudioInStandbyToStartup. */
extern int gx_audio_in_set_interrupt_enable(unsigned int, unsigned int);
void open_cfw_gx8002_audio_input_suspend(void)
{
    gx_audio_in_set_interrupt_enable(0x20007, 0);
    gx_audio_in_set_interrupt_enable(0x10000, 1);
}
void open_cfw_gx8002_audio_input_standby_startup(void)
{
    struct flags_byte { unsigned char last_vad : 4; unsigned char startup : 4; };
    volatile struct flags_byte *flags = (void *)0x2002ecc0;
    flags->startup = 1;
    gx_audio_in_set_interrupt_enable(0x30007, 1);
}
