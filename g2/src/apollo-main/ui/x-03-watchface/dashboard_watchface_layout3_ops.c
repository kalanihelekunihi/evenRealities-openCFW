/* Dashboard watchface layout3 ops-table entries, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_watchface_layout3.c
 * (log tag "dashboard.wf.l3"). Native 0x5baa44..0x5baa75 (ops +0x2c, ring
 * battery level) and 0x5bab24..0x5bab2b (ops +0x20, BLE state); literal pool
 * 0x5baa78..0x5bab23 shared with ui/a-64-dashboard-watchface, where
 * apollo_main.tsv files both functions as pool. Ops table ROM 0x714008. */
#include <stdint.h>

extern void *g2_layout3_ring_battery_img; /* RAM 0x200744a0 */

extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *object); /* lv_obj_is_valid */
extern uint8_t ux_ring_connected_47d9cc(void);
extern void audio_uart_page_498680(void *image, const void *src);    /* lv_image_set_src */
extern const void *layout3_ring_battery_dsc_5b9d66(uint8_t level);
extern void layout3_apply_ble_5b9fd6(uint32_t connected);

void layout3_set_ring_battery_5baa44(uint8_t level);
void layout3_set_ble_connected_5bab24(uint32_t connected);

/* ops +0x2c: ring battery icon, only while the ring is connected. */
void layout3_set_ring_battery_5baa44(uint8_t level)
{
    if (g2_layout3_ring_battery_img == 0 ||
        audio_terminal_ui_object_valid_43e2ea(g2_layout3_ring_battery_img) == 0u)
        return;
    if (ux_ring_connected_47d9cc() == 0u)
        return;
    audio_uart_page_498680(g2_layout3_ring_battery_img, layout3_ring_battery_dsc_5b9d66(level));
}

/* ops +0x20 */
void layout3_set_ble_connected_5bab24(uint32_t connected)
{
    layout3_apply_ble_5b9fd6(connected);
}
