/* Dashboard watchface layout1 slot refresh and BLE state ops, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_watchface_layout1.c
 * (log tag "dashboard.wf.l1"). Native 0x5b87ec..0x5b8843 (slot text
 * callback, referenced from pool 0x5b89ec), 0x5b8844..0x5b8851 (ops +0x34),
 * 0x5b8852..0x5b885f (ops +0x38) and 0x5b8880..0x5b8985 (ops +0x20); literal
 * pool 0x5b87cc..0x5b89ef shared with ui/a-63-watchface-layout1 and
 * ui/a-64-dashboard-watchface. apollo_main.tsv files these ranges as literal
 * pool. Ops table ROM 0x713f54 (ui/a-39-dashboard-watchface-manager).
 *
 * Complication kinds 2 and 3 are the two weather text complications
 * (weather service strings at +0x80 / +0x5c, "--" without weather data) as
 * formatted by layout2_slot_text_5b8bc8. */
#include <stdint.h>
#include <stddef.h>
#include "../a-63-watchface-layout1/dashboard_watchface_layout1.h"

#define LV_OBJ_FLAG_HIDDEN 0x1u
#define SLOT_TEXT_SIZE 32u

extern void *g2_layout1_ble_off_cont; /* RAM 0x20074454 */

extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *object);     /* lv_obj_is_valid */
extern void audio_uart_page_43ded4(void *object, uint32_t flags);         /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *object, uint32_t flags);         /* lv_obj_remove_flag */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern const char *audio_uart_page_49942e(void *label, const char *text); /* lv_label_set_text */
extern void layout2_slot_icon_refresh_5b8d20(g2_wf_slot_t *slot);
extern void layout2_slot_text_5b8bc8(uint8_t kind, char *buf, uint32_t size);

void layout1_slot_text_refresh_5b87ec(g2_wf_slot_t *slot, const void *arg);
void layout1_refresh_kind2_slots_5b8844(void);
void layout1_refresh_kind3_slots_5b8852(void);
void layout1_set_ble_connected_5b8880(uint32_t connected);

static uint32_t obj_live(void *obj)
{
    return obj != NULL && audio_terminal_ui_object_valid_43e2ea(obj) == 1u;
}

static void show(void *obj)
{
    if (obj_live(obj))
        audio_uart_page_43dfa4(obj, LV_OBJ_FLAG_HIDDEN);
}

static void hide(void *obj)
{
    if (obj_live(obj))
        audio_uart_page_43ded4(obj, LV_OBJ_FLAG_HIDDEN);
}

/* layout1_slots_for_kind_5b845c callback: refresh icon and text of a slot. */
void layout1_slot_text_refresh_5b87ec(g2_wf_slot_t *slot, const void *arg)
{
    char text[SLOT_TEXT_SIZE];

    (void)arg;
    if (slot == NULL)
        return;
    if (obj_live(slot->icon))
        layout2_slot_icon_refresh_5b8d20(slot);
    if (obj_live(slot->label)) {
        (void)aeabi_memset_43c0e4(text, sizeof(text), 0);
        layout2_slot_text_5b8bc8(slot->kind, text, sizeof(text));
        (void)audio_uart_page_49942e(slot->label, text);
    }
    layout1_slot_layout_5b7a4c(slot);
}

/* ops +0x34 */
void layout1_refresh_kind2_slots_5b8844(void)
{
    layout1_slots_for_kind_5b845c(2u, layout1_slot_text_refresh_5b87ec, NULL);
}

/* ops +0x38 */
void layout1_refresh_kind3_slots_5b8852(void)
{
    layout1_slots_for_kind_5b845c(3u, layout1_slot_text_refresh_5b87ec, NULL);
}

/* ops +0x20: connected shows both complication slots and hides the
 * "BLE off" container; disconnected does the opposite. */
void layout1_set_ble_connected_5b8880(uint32_t connected)
{
    if (connected != 0u) {
        show(g2_layout1_slot_a.icon);
        show(g2_layout1_slot_a.label);
        hide(g2_layout1_ble_off_cont);
        show(g2_layout1_slot_b.icon);
        show(g2_layout1_slot_b.label);
    } else {
        hide(g2_layout1_slot_a.icon);
        hide(g2_layout1_slot_a.label);
        show(g2_layout1_ble_off_cont);
        hide(g2_layout1_slot_b.icon);
        hide(g2_layout1_slot_b.label);
    }
}
