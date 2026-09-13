/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* Internal40-byte layout recovered from aout_i2s_config, distinct from
 * the public I2S structure. Names track register bits until callers resolve
 * their meaning. Public wrapper e1f0 establishes word6=bclk, word3=PCM
 * length, word4=data format. Config words0 and5 are not read by this helper. */
typedef union {
    uint32_t word;
    struct { unsigned data_format:2,pcm_length:2,field4:3,pad7:2,field9:1,pad10:4,
                      field14:1,field15:1,bclk:1,upper:15; } config;
    struct { unsigned low:31,enable:1; } fixed;
} i2s_word;
void open_cfw_gx8002_aout_i2s_config(volatile uint32_t *base,
                                    const volatile uint32_t *config)
{
    i2s_word edit;
#define UPDATE(field,index) do { edit.word=base[1]; edit.config.field=config[index]; base[1]=edit.word; } while (0)
    UPDATE(bclk,6);
    UPDATE(field15,7);
    UPDATE(field14,8);
    UPDATE(field9,1);
    UPDATE(field4,2);
    UPDATE(pcm_length,3);
    UPDATE(data_format,4);
#undef UPDATE
    edit.word=base[4];
    edit.fixed.enable=config[9];
    base[4]=edit.word;
    uint32_t word=base[4];
    base[4]=(word&0xff000000u)|1024u;
}
