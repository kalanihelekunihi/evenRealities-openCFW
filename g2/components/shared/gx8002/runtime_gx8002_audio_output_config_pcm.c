/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_out/gx_audio_out_v2.h>
extern int printf_(const char *, ...);
extern void open_cfw_gx8002_aout_i2s_config(uint32_t, void *);
extern void open_cfw_gx8002_aout_dac_config(uint32_t, void *);
extern void open_cfw_gx8002_aout_lodac(void);
const char open_cfw_gx8002_aout_pcm_clock_diagnostic[]
    __attribute__((section(".rodata.aout_pcm_clock_diagnostic"))) =
    "The current clock and sampling rate do not match. \n please,Please use audio with sampling rates of 8k, 16k, and 48k!\n";
/* Reconstructed stock e2c4. Config must be readable; nonzero module_freq
 * requires nonzero sample_rate. Preserve the original diagnostic wording. */
int open_cfw_gx8002_aout_config_pcm(void *handle, const volatile GX_AUDIO_OUT_PCM *config)
{
    uint32_t bits=config->bits;
    if (bits!=16 && bits!=32) return -1;
    uint32_t frequency=config->module_freq;
    uint32_t ratio=0;
    uint32_t remainder=0;
    if (frequency) {
        uint32_t rate=config->sample_rate;
        ratio=frequency/rate;
        remainder=frequency-ratio*rate;
    }
    if (!frequency || remainder) {
        printf_(open_cfw_gx8002_aout_pcm_clock_diagnostic);
        return -1;
    }
    uint32_t mode;
    switch (ratio) {
    case 128:mode=3;break;
    case 192:mode=7;break;
    case 256:mode=0;break;
    case 384:mode=4;break;
    case 512:mode=1;break;
    case 768:mode=5;break;
    case 1024:mode=2;break;
    case 1536:mode=6;break;
    default:return -1;
    }
    uint8_t *state=handle;
    uint32_t *settings=*(uint32_t *volatile *)(state+48);
    *(volatile uint32_t *)(settings+4)=mode;
    *(volatile uint8_t *)(state+25)=(uint8_t)(bits>>3);
    uint32_t multiple_channels=config->channels!=1;
    volatile uint32_t *sdc=(volatile uint32_t *)0xa0b80000u;
    *sdc=(*sdc&~15u)|(bits==16?8u:0u);
    *sdc=(*sdc&~64u)|(multiple_channels<<6);
    uint32_t word=*sdc;
    *sdc=(word&~128u)|((config->interlace!=0)<<7);
    word=*sdc;
    uint32_t endian=config->endian!=0;
    settings=*(uint32_t *volatile *)(state+48);
    *sdc=(word&~48u)|(endian<<4);
    open_cfw_gx8002_aout_i2s_config(0xa0b00000u,(uint8_t *)settings+8);
    settings=*(uint32_t *volatile *)(state+48);
    open_cfw_gx8002_aout_dac_config(0xa0b00000u,(uint8_t *)settings+48);
    open_cfw_gx8002_aout_lodac();
    return 0;
}
