/* SPDX-License-Identifier: MIT
 * Image-A XIP mode callbacks and queue initializer, native addresses
 * 0x10208624/34/44/4c/70 and 0x10206f9c. Stock callback error status
 * is the return of its audio-input initializer at 0x102073bc.
 */
#include <stdint.h>

extern void gx8002_xip_tws_publish_10206c24(const char *, ...);
extern void gx8002_xip_memset_102099cc(void *, uint32_t, uint32_t);
extern void gx8002_xip_buffer_initialize_10206dc0(void);
extern void gx8002_xip_kws_done_10206dac(void);
extern uint32_t gx8002_xip_audio_input_done_102073f8(void);
extern void gx8002_xip_max_kws_initialize_10208944(void);
extern uint32_t gx8002_resident_pmu_wakeup_source_24940(void);
extern uint32_t gx8002_resident_active_snpu_callback_26340(
    uint32_t, uint32_t, uint32_t);
extern uint32_t gx8002_xip_kws_initialize_10206d90(
    uint32_t (*callback)(uint32_t,uint32_t,uint32_t), uint32_t source);
extern uint32_t gx8002_resident_tws_audio_callback_263dc(int32_t);
extern uint32_t gx8002_xip_audio_input_initialize_102073bc(
    uint32_t (*callback)(int32_t));
extern void gx8002_xip_audio_standby_startup_10207660(void);

void gx8002_xip_queue_initialize_10206f9c(
    volatile uint32_t *queue, uint32_t storage, int32_t capacity,
    int32_t element_size)
{
    queue[4] = (uint32_t)element_size;
    queue[2] = storage;
    queue[3] = (uint32_t)element_size *
               (uint32_t)(capacity / element_size);
    queue[0] = 0u;
    queue[1] = 0u;
}

void gx8002_xip_idle_done_10208624(void)
{
    gx8002_xip_tws_publish_10206c24("[IDLE]Exit IDLE mode\n");
}

uint32_t gx8002_xip_idle_initialize_10208634(uint32_t unused)
{
    (void)unused;
    gx8002_xip_tws_publish_10206c24("[IDLE]Init IDLE mode\n");
    return 0u;
}

void gx8002_xip_tws_buffer_initialize_10208644(void)
{
    gx8002_xip_buffer_initialize_10206dc0();
}

void gx8002_xip_tws_done_1020864c(void)
{
    gx8002_xip_memset_102099cc(
        (void *)(uintptr_t)UINT32_C(0x2002e6ec), 0u, 20u);
    gx8002_xip_kws_done_10206dac();
    gx8002_xip_audio_input_done_102073f8();
    gx8002_xip_tws_publish_10206c24("[LVP_TWS]Exit TWS mode\n");
}

uint32_t gx8002_xip_tws_initialize_10208670(uint32_t argument)
{
    gx8002_xip_queue_initialize_10206f9c(
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e6ec),
        UINT32_C(0x2002e700), 56, 8);
    gx8002_xip_max_kws_initialize_10208944();
    uint32_t source = gx8002_resident_pmu_wakeup_source_24940();
    (void)gx8002_xip_kws_initialize_10206d90(
        gx8002_resident_active_snpu_callback_26340, source);
    if (argument == 0xffffu && source >= 2u) {
        gx8002_xip_audio_standby_startup_10207660();
    } else if (gx8002_xip_audio_input_initialize_102073bc(
                   gx8002_resident_tws_audio_callback_263dc) != 0u) {
        gx8002_xip_tws_publish_10206c24(
            "[LVP_TWS]LvpAudioInInit Failed\n");
        return UINT32_MAX;
    }
    volatile uint32_t *const queue =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e6ec);
    queue[0x4cu / 4u] = 2u;
    queue[0x50u / 4u] = 50u;
    return 0u;
}
