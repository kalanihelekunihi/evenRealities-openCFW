/* Image-B native 0x10006a80..0x10006c25: audio output dispatch wrappers.
 * The active table pointer is mutable SRAM 0x20017640; the init fallback
 * table is product initialized SRAM 0x20016cb8. This source does not supply
 * either table's missing initialized contents or final placement.
 * Native SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>

extern int gx8002_image_b_heap_log_10009934(const char *, ...);

static volatile uint32_t *const active_table =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20017640);

static uint32_t slot(uint32_t table, uint32_t offset)
{
    return *(volatile uint32_t *)(uintptr_t)(table + offset);
}

static uint32_t missing_table(const char *name, uint32_t line)
{
    (void)gx8002_image_b_heap_log_10009934(
        "[AOUT ERROR] %s %d\n", name, line);
    return UINT32_MAX;
}

uint32_t gx8002_image_b_audio_out_state_address_10006a80(void)
{
    return UINT32_C(0x20016d0c);
}

uint32_t gx8002_image_b_audio_out_alloc_10006a88(uint32_t mode)
{
    uint32_t table = *active_table;
    if (table == 0u) return missing_table("gx_audio_out_alloc_playback", 234u);
    uint32_t target = slot(table, 0u);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t))(uintptr_t)target)(mode);
}

uint32_t gx8002_image_b_audio_out_config_buffer_10006abc(
    uint32_t handle, uint32_t descriptor)
{
    uint32_t table = *active_table;
    if (table == 0u) return missing_table("gx_audio_out_config_buffer", 255u);
    uint32_t target = slot(table, 0x18u);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t, uint32_t))(uintptr_t)target)(
            handle, descriptor);
}

uint32_t gx8002_image_b_audio_out_config_pcm_10006af0(
    uint32_t handle, uint32_t descriptor)
{
    uint32_t table = *active_table;
    if (table == 0u) return missing_table("gx_audio_out_config_pcm", 265u);
    uint32_t target = slot(table, 0x1cu);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t, uint32_t))(uintptr_t)target)(
            handle, descriptor);
}

uint32_t gx8002_image_b_audio_out_config_cb_10006b28(
    uint32_t handle, uint32_t callbacks)
{
    uint32_t table = *active_table;
    if (table == 0u) return missing_table("gx_audio_out_config_cb", 295u);
    uint32_t target = slot(table, 0x28u);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t, uint32_t))(uintptr_t)target)(
            handle, callbacks);
}

uint32_t gx8002_image_b_audio_out_push_frame_10006b60(
    uint32_t handle, uint32_t frame)
{
    uint32_t table = *active_table;
    if (table == 0u) return missing_table("gx_audio_out_push_frame", 305u);
    uint32_t target = slot(table, 0x2cu);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t, uint32_t))(uintptr_t)target)(handle, frame);
}

uint32_t gx8002_image_b_audio_out_set_db_10006b98(
    uint32_t handle, int32_t db)
{
    uint32_t table = *active_table;
    if (table == 0u) return missing_table("gx_audio_out_set_db", 325u);
    uint32_t target = slot(table, 0x38u);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t, int32_t))(uintptr_t)target)(handle, db);
}

uint32_t gx8002_image_b_audio_out_set_channel_10006bd0(
    uint32_t handle, uint32_t channel)
{
    uint32_t table = *active_table;
    if (table == 0u) return missing_table("gx_audio_out_set_channel", 365u);
    uint32_t target = slot(table, 0x48u);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t, uint32_t))(uintptr_t)target)(
            handle, channel);
}

uint32_t gx8002_image_b_audio_out_init_10006c08(uint32_t mode)
{
    uint32_t table = *active_table;
    if (table == 0u) {
        table = UINT32_C(0x20016cb8);
        *active_table = table;
    }
    uint32_t target = slot(table, 4u);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t))(uintptr_t)target)(mode);
}
