/* Dashboard main screen settings/weather apply, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_DashBaord_Main_Screen.c.
 * Native 0x4e8970..0x4e8a5f (literal pool 0x4e9358..0x4e9363). Split from
 * ui_dashboard_main_screen.c because the weather temperature is a float
 * handed to the watch face in s0 (hard-float call, single precision).
 *
 * Record (0xa0 bytes, same layout as the dashboard state block at RAM
 * 0x200e3e80): +0x00 two words, +0x08 u16, +0x0a u16 tile count (<= 6),
 * +0x0c u16 tiles[6], +0x18 u16 widget count (<= 6), +0x1a u8 widgets[6],
 * +0x20 weather block (0x80 bytes: +0x20 u8 valid, +0x24 float temperature,
 * +0x2a u16 weather icon code). */
#include <stdint.h>
#include <stddef.h>

#define DASH_STATE_LEN 0xa0u
#define DASH_MAX_TILES 6u

extern uint8_t g2_dashboard_status_rx_201201b4[DASH_STATE_LEN]; /* RAM 0x201201b4 */
extern uint8_t g2_dashboard_state[];                      /* RAM 0x200e3e80, 0xa0 bytes */
extern void *g2_dashboard_mutex_200743a8;                 /* RAM 0x200743a8 osMutexId */

extern int32_t osMutexAcquire(void *mutex, uint32_t timeout); /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                   /* 0x44981c */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);
extern uint8_t svc_universal_setting_get_temperature_unit_466512(void); /* 1 = Fahrenheit */
extern int32_t ui_common_api_fn_00509f86(void);  /* battery percent for the label */
extern uint8_t ui_common_api_fn_00509f8e(void);  /* battery percent for the icon */
extern __attribute__((pcs("aapcs-vfp"))) void
dashboard_watchface_manager_call_14(uint16_t weather_icon, uint8_t weather_valid,
                                    uint8_t fahrenheit, float temperature); /* 0x50067a */
extern void dashboard_watchface_manager_call_34(void);        /* 0x500746 */
extern void dashboard_watchface_manager_call_38(void);        /* 0x500760 */
extern void dashboard_watchface_manager_call_1c(void);        /* 0x5006f8 */
extern void dashboard_watchface_manager_set_battery(uint8_t percent); /* 0x500696 */

void dashboard_status_data_apply_4e8970(const uint8_t *data, uint32_t len);

#define U16(p, o) (*(uint16_t *)(void *)((p) + (o)))
#define U32(p, o) (*(uint32_t *)(void *)((p) + (o)))

/* Event code 1: copy a settings/weather record into the dashboard state (when
 * one is given) and refresh the watch face from the state block. */
void dashboard_status_data_apply_4e8970(const uint8_t *data, uint32_t len)
{
    uint8_t *const rx = g2_dashboard_status_rx_201201b4;
    uint8_t *const st = g2_dashboard_state;

    if (len != 0u) {
        aeabi_memset_43c0e4(rx, DASH_STATE_LEN, 0);
        audio_queue_copy_bytes(rx, data, DASH_STATE_LEN);
        U32(st, 0x00) = U32(rx, 0x00);
        U32(st, 0x04) = U32(rx, 0x04);
        U16(st, 0x08) = U16(rx, 0x08);
        U16(st, 0x0a) = U16(rx, 0x0a);
        if (U16(st, 0x0a) > DASH_MAX_TILES)
            U16(st, 0x0a) = DASH_MAX_TILES;
        for (int32_t i = 0; i < (int32_t)U16(st, 0x0a); i++)
            U16(st, 0x0c + 2 * i) = U16(rx, 0x0c + 2 * i);
        U16(st, 0x18) = U16(rx, 0x18);
        if (U16(st, 0x18) > DASH_MAX_TILES)
            U16(st, 0x18) = DASH_MAX_TILES;
        for (int32_t i = 0; i < (int32_t)U16(st, 0x18); i++)
            st[0x1a + i] = rx[0x1a + i];
        aeabi_memcpy4_439c04(st + 0x20, rx + 0x20, 0x80u);
    }

    (void)osMutexAcquire(g2_dashboard_mutex_200743a8, 0xffffffffu);
    uint16_t icon = U16(st, 0x2a);
    float temperature = *(const float *)(const void *)(st + 0x24);
    uint8_t valid = st[0x20];
    (void)osMutexRelease(g2_dashboard_mutex_200743a8);
    dashboard_watchface_manager_call_14(icon, valid,
                                        svc_universal_setting_get_temperature_unit_466512() == 1u,
                                        temperature);
    dashboard_watchface_manager_call_34();
    dashboard_watchface_manager_call_38();
    (void)ui_common_api_fn_00509f86();
    dashboard_watchface_manager_call_1c();
    dashboard_watchface_manager_set_battery(ui_common_api_fn_00509f8e());
}
