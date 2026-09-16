/* SPDX-License-Identifier: MIT */
/* Backup LvpAudioInSuspend/Resume, without energy-VAD configuration.
 * Masks correspond to the pinned SDK's PCM0/PCM1/logfbank and FFT-VAD bits. */
#include <stdint.h>
extern int open_cfw_gx8002_audio_interrupt_enable(uint32_t mask,unsigned enable);
void open_cfw_gx8002_backup_audio_suspend(void)
{
    open_cfw_gx8002_audio_interrupt_enable(UINT32_C(0x20007),0);
    open_cfw_gx8002_audio_interrupt_enable(UINT32_C(0x10000),1);
}
void open_cfw_gx8002_backup_audio_resume(void)
{
    open_cfw_gx8002_audio_interrupt_enable(UINT32_C(0x30007),1);
}
