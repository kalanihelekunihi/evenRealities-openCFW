/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
/* Internal hw.o ABI, distinct from the public 24-byte GX_AUDIO_OUT_DAC.
 * Bytes24..35 configure three additional fields; their semantic names remain
 * unresolved. Sample counts are read as bytes by stock, despite public shorts. */
typedef struct {
    uint32_t low_enable;
    uint8_t low_count, low_count_padding;
    uint16_t low_value, low_channel, low_padding;
    uint32_t high_enable;
    uint8_t high_count, high_count_padding;
    uint16_t high_value, high_channel, high_padding;
    uint32_t extra_enable, extra_field23, extra_field16;
} dac_internal;
_Static_assert(sizeof(dac_internal)==36,"Internal DAC ABI");
_Static_assert(offsetof(dac_internal,extra_enable)==24,"Extra DAC fields");
typedef union {
    uint32_t word;
    struct { unsigned value:16,count:8,channel:2,reserved:5,enable:1; } detect;
    struct { unsigned low:16,field16:3,middle:4,field23:3,upper:5,enable:1; } extra;
} dac_word;
void open_cfw_gx8002_aout_dac_config(volatile uint32_t *base,
                                    const volatile dac_internal *config)
{
    dac_word edit;
#define UPDATE(reg,field,value) do { edit.word=base[(reg)/4]; edit.field=(value); base[(reg)/4]=edit.word; } while (0)
    UPDATE(0x18,detect.enable,config->low_enable);
    UPDATE(0x18,detect.count,config->low_count);
    UPDATE(0x18,detect.value,config->low_value);
    UPDATE(0x18,detect.channel,config->low_channel);
    UPDATE(0x1c,detect.enable,config->high_enable);
    UPDATE(0x1c,detect.count,config->high_count);
    UPDATE(0x1c,detect.value,config->high_value);
    UPDATE(0x1c,detect.channel,config->high_channel);
    UPDATE(0x2c,extra.enable,config->extra_enable);
    UPDATE(0x2c,extra.field23,config->extra_field23);
    UPDATE(0x2c,extra.field16,config->extra_field16);
#undef UPDATE
}
