/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10205374 and 0x1020537c..0x10205599.
 * The wrappers forward their original argument registers through a
 * product-owned SRAM operation table. No table contents are fabricated.
 * Error format/name literals are exact stock XIP strings.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);

static volatile uint32_t *const active_table =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002734c);

static uint32_t error(const char *name, uint32_t line)
{
    (void)gx8002_xip_tws_publish_10206c24(
        "[AOUT ERROR] %s %d\n", name, line);
    return UINT32_MAX;
}

static uint32_t slot(uint32_t table, uint32_t offset)
{
    return *(volatile uint32_t *)(uintptr_t)(table + offset);
}

uint32_t gx8002_xip_aout_select_hw_config_10205374(void)
{
    return UINT32_C(0x20026c1c);
}

uint32_t gx8002_xip_audio_out_alloc_playback_1020537c(uint32_t mode)
{
    uint32_t table = *active_table;
    if (table == 0u) return error("gx_audio_out_alloc_playback", 234u);
    uint32_t target = slot(table, 0u);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t))(uintptr_t)target)(mode);
}

uint32_t gx8002_xip_audio_out_free_102053b0(uint32_t handle)
{
    uint32_t table = *active_table;
    if (table == 0u) return error("gx_audio_out_free", 245u);
    uint32_t target = slot(table, 0x14u);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t))(uintptr_t)target)(handle);
}

uint32_t gx8002_xip_audio_out_config_buffer_102053e4(
    uint32_t handle, uint32_t descriptor)
{
    uint32_t table = *active_table;
    if (table == 0u) return error("gx_audio_out_config_buffer", 255u);
    uint32_t target = slot(table, 0x18u);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t, uint32_t))(uintptr_t)target)(
            handle, descriptor);
}

uint32_t gx8002_xip_audio_out_config_pcm_10205418(
    uint32_t handle, uint32_t descriptor)
{
    uint32_t table = *active_table;
    if (table == 0u) return error("gx_audio_out_config_pcm", 265u);
    uint32_t target = slot(table, 0x1cu);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t, uint32_t))(uintptr_t)target)(
            handle, descriptor);
}

uint32_t gx8002_xip_audio_out_config_cb_10205450(
    uint32_t handle, uint32_t callbacks)
{
    uint32_t table = *active_table;
    if (table == 0u) return error("gx_audio_out_config_cb", 295u);
    uint32_t target = slot(table, 0x28u);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t, uint32_t))(uintptr_t)target)(
            handle, callbacks);
}

uint32_t gx8002_xip_audio_out_push_frame_10205488(
    uint32_t handle, uint32_t frame)
{
    uint32_t table = *active_table;
    if (table == 0u) return error("gx_audio_out_push_frame", 305u);
    uint32_t target = slot(table, 0x2cu);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t, uint32_t))(uintptr_t)target)(
            handle, frame);
}

uint32_t gx8002_xip_audio_out_set_db_102054c0(
    uint32_t handle, int32_t db)
{
    uint32_t table = *active_table;
    if (table == 0u) return error("gx_audio_out_set_db", 325u);
    uint32_t target = slot(table, 0x38u);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t, int32_t))(uintptr_t)target)(handle, db);
}

uint32_t gx8002_xip_audio_out_set_channel_102054f8(
    uint32_t handle, uint32_t channel)
{
    uint32_t table = *active_table;
    if (table == 0u) return error("gx_audio_out_set_channel", 365u);
    uint32_t target = slot(table, 0x48u);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t, uint32_t))(uintptr_t)target)(
            handle, channel);
}

uint32_t gx8002_xip_audio_out_init_10205530(uint32_t mode)
{
    if (*active_table == 0u) *active_table = UINT32_C(0x20026bc8);
    uint32_t table = *active_table;
    if (table == 0u) return error("gx_audio_out_init", 377u);
    uint32_t target = slot(table, 4u);
    return target == 0u ? 0u :
        ((uint32_t (*)(uint32_t))(uintptr_t)target)(mode);
}

uint32_t gx8002_xip_audio_out_exit_10205574(void)
{
    uint32_t table = *active_table;
    if (table == 0u) return error("gx_audio_out_exit", 387u);
    uint32_t target = slot(table, 8u);
    return target == 0u ? 0u :
        ((uint32_t (*)(void))(uintptr_t)target)();
}
