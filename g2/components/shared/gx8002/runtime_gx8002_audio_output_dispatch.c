/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
#include <gx_audio_out/gx_audio_out_v2.h>
/* Dispatch entries use the reconstructed function signatures. */
extern void * open_cfw_gx8002_aout_alloc_playback(unsigned int);
extern int open_cfw_gx8002_aout_init(uint32_t);
extern int open_cfw_gx8002_aout_exit(void);
extern int open_cfw_gx8002_aout_suspend(void *);
extern int open_cfw_gx8002_aout_resume(void *);
extern int open_cfw_gx8002_aout_free(void *);
extern int open_cfw_gx8002_aout_config_buffer(int, const volatile uint32_t *);
extern int open_cfw_gx8002_aout_config_pcm(void *, const volatile GX_AUDIO_OUT_PCM *);
extern int open_cfw_gx8002_aout_config_i2s(void *, const GX_AUDIO_OUT_I2S *);
extern int open_cfw_gx8002_aout_config_dac(void *, const GX_AUDIO_OUT_DAC *);
extern int open_cfw_gx8002_aout_config_cb(void *, const volatile GX_AUDIO_OUT_CALLBACK *);
extern int open_cfw_gx8002_aout_push_frame(void *, const void *);
extern int open_cfw_gx8002_aout_drain_frame(void *);
extern int open_cfw_gx8002_aout_set_db(void *, int16_t);
extern int open_cfw_gx8002_aout_get_db(void *, volatile int16_t *);
extern int open_cfw_gx8002_aout_set_mute(void *, int);
extern int open_cfw_gx8002_aout_get_mute(void *);
extern int open_cfw_gx8002_aout_set_channel(int, unsigned int);
extern int open_cfw_gx8002_aout_set_fixed_src(int, short);
extern uint32_t open_cfw_gx8002_aout_get_sdc_addr(int);
typedef struct {
    __typeof__(&open_cfw_gx8002_aout_alloc_playback) alloc_playback;
    __typeof__(&open_cfw_gx8002_aout_init) init;
    __typeof__(&open_cfw_gx8002_aout_exit) exit;
    __typeof__(&open_cfw_gx8002_aout_suspend) suspend;
    __typeof__(&open_cfw_gx8002_aout_resume) resume;
    __typeof__(&open_cfw_gx8002_aout_free) free;
    __typeof__(&open_cfw_gx8002_aout_config_buffer) config_buffer;
    __typeof__(&open_cfw_gx8002_aout_config_pcm) config_pcm;
    __typeof__(&open_cfw_gx8002_aout_config_i2s) config_i2s;
    __typeof__(&open_cfw_gx8002_aout_config_dac) config_dac;
    __typeof__(&open_cfw_gx8002_aout_config_cb) config_cb;
    __typeof__(&open_cfw_gx8002_aout_push_frame) push_frame;
    void (*reserved)(void);
    __typeof__(&open_cfw_gx8002_aout_drain_frame) drain_frame;
    __typeof__(&open_cfw_gx8002_aout_set_db) set_db;
    __typeof__(&open_cfw_gx8002_aout_get_db) get_db;
    __typeof__(&open_cfw_gx8002_aout_set_mute) set_mute;
    __typeof__(&open_cfw_gx8002_aout_get_mute) get_mute;
    __typeof__(&open_cfw_gx8002_aout_set_channel) set_channel;
    __typeof__(&open_cfw_gx8002_aout_set_fixed_src) set_fixed_src;
    __typeof__(&open_cfw_gx8002_aout_get_sdc_addr) get_sdc_addr;
} output_dispatch;
_Static_assert(sizeof(output_dispatch)==84,"Dispatch size");
_Static_assert(offsetof(output_dispatch,reserved)==48,"Reserved slot");
output_dispatch open_cfw_gx8002_aout_dispatch={
    .alloc_playback=open_cfw_gx8002_aout_alloc_playback,
    .init=open_cfw_gx8002_aout_init,
    .exit=open_cfw_gx8002_aout_exit,
    .suspend=open_cfw_gx8002_aout_suspend,
    .resume=open_cfw_gx8002_aout_resume,
    .free=open_cfw_gx8002_aout_free,
    .config_buffer=open_cfw_gx8002_aout_config_buffer,
    .config_pcm=open_cfw_gx8002_aout_config_pcm,
    .config_i2s=open_cfw_gx8002_aout_config_i2s,
    .config_dac=open_cfw_gx8002_aout_config_dac,
    .config_cb=open_cfw_gx8002_aout_config_cb,
    .push_frame=open_cfw_gx8002_aout_push_frame,
    .drain_frame=open_cfw_gx8002_aout_drain_frame,
    .set_db=open_cfw_gx8002_aout_set_db,
    .get_db=open_cfw_gx8002_aout_get_db,
    .set_mute=open_cfw_gx8002_aout_set_mute,
    .get_mute=open_cfw_gx8002_aout_get_mute,
    .set_channel=open_cfw_gx8002_aout_set_channel,
    .set_fixed_src=open_cfw_gx8002_aout_set_fixed_src,
    .get_sdc_addr=open_cfw_gx8002_aout_get_sdc_addr,
};
