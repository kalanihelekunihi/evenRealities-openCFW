/* Dashboard watchface layout2/layout4 slot helpers (product code; the stock
 * TUs are named by their log strings "layout2_create" / "layout4_pick_...").
 * Native 0x5b8d20..0x5b8d5f, 0x5b8e1a..0x5b8e49, 0x5b8f18..0x5b90ad
 * (layout2) and 0x5bab76..0x5baba5 (layout4).
 *
 * The inventory filed these rows under LVGL modules by call topology; they are
 * first-party callers of LVGL, not LVGL code. LVGL callees keep the names the
 * rest of g2/src already uses (audio_uart_page_<addr>); their LVGL identity is
 * noted next to each declaration. */
#include <stdint.h>
#include <stddef.h>

/* One 12-byte record per complication slot, RAM 0x200005e8 (3 slots). */
typedef struct {
    void *icon;     /* +0x0 lv_image */
    void *label;    /* +0x4 lv_label */
    uint8_t kind;   /* +0x8 complication kind (0 = none) */
    uint8_t active; /* +0x9 */
    uint8_t pad[2];
} g2_layout2_slot_t;
_Static_assert(sizeof(g2_layout2_slot_t) == 12, "layout2 slot record");

extern g2_layout2_slot_t g2_layout2_slots[3];   /* RAM 0x200005e8 */
extern void *g2_layout2_slot_conts[3];          /* RAM 0x20073fb4 */
extern void *g2_layout2_parent;                 /* RAM 0x2007445c */
extern uint8_t g2_layout2_align_setting;        /* RAM 0x20074fa9 */
extern uint8_t g2_layout2_slot_count;           /* RAM 0x20074faa */
extern uint8_t g2_layout4_align_setting;        /* RAM 0x20074fae */
extern uint8_t g2_dashboard_state[];            /* RAM 0x200e3e80; +0x2a u16 icon code */
extern uint32_t audio_uart_ring_primary_head_cell; /* RAM 0x200746dc: active lv_font_t * */

/* LVGL (core at 0x43xxxx..0x49xxxx). */
extern uint32_t audio_uart_page_43de82(uint32_t parent);                 /* lv_obj_create */
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);       /* lv_obj_set_size */
extern void audio_uart_page_43f506(uint32_t, uint32_t);                 /* lv_obj_set_width */
extern void audio_uart_page_43f568(uint32_t, uint32_t);                 /* lv_obj_set_height */
extern void audio_uart_page_43f09a(uint32_t, uint32_t, uint32_t);       /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(uint32_t object, uint32_t x);        /* lv_obj_set_x */
extern void audio_uart_page_43f142(uint32_t object, uint32_t y);        /* lv_obj_set_y */
extern void audio_uart_page_43f6ac(uint32_t object, uint32_t align);    /* lv_obj_set_align */
extern void audio_uart_page_43f6d6(uint32_t, uint32_t, uint32_t,
                                   uint32_t, uint32_t);                 /* lv_obj_align_to */
extern void audio_uart_page_43ded4(uint32_t, uint32_t);                 /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *, uint32_t);                   /* lv_obj_remove_flag */
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);       /* set_style_bg_opa */
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);       /* set_style_border_width */
extern void audio_uart_page_44133a(uint32_t, uint32_t, uint32_t);       /* set_style_outline_width */
extern void audio_uart_page_441386(uint32_t, uint32_t, uint32_t);       /* set_style_shadow_width */
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);       /* set_style_radius */
extern uint32_t audio_uart_page_44104c(uint32_t);                       /* lv_color_hex */
extern void audio_uart_page_44140e(uint32_t, uint32_t, uint32_t);       /* set_style_text_color */
extern void audio_uart_page_44142e(uint32_t, uint32_t, uint32_t);       /* set_style_text_opa */
extern void audio_uart_page_44143e(uint32_t, uint32_t, uint32_t);       /* set_style_text_font */
extern uint32_t audio_uart_page_498668(uint32_t parent);                /* lv_image_create */
extern void audio_uart_page_498680(void *, const void *);               /* lv_image_set_src */
extern uint32_t audio_uart_page_499416(uint32_t parent);                /* lv_label_create */
extern const char *audio_uart_page_49942e(uint8_t *, const char *);     /* lv_label_set_text */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);

/* Product helpers in the same TUs. */
extern void lv_obj_set_style_pad_all_5b8dd0(uint32_t obj, uint32_t value, uint32_t selector);
extern const void *dashboard_icon_src_by_code_50f810(uint32_t code);
extern const void *layout2_slot_icon_src_5b89f0(uint8_t kind);
extern void layout2_slot_text_5b8bc8(uint8_t kind, char *buf, uint32_t size);
extern uint8_t layout2_align_from_setting_5b8e02(uint8_t setting);
extern int32_t layout2_slot_y_5b8e4a(int32_t row);
extern int32_t layout2_slot_row_5b8e5e(uint32_t slot, int32_t count);
extern uint8_t layout4_align_from_setting_5bab5e(uint8_t setting);

#define LV_SIZE_CONTENT 0x3fffffffu
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_ALIGN_OUT_RIGHT_MID 20u

void layout2_slot_icon_refresh_5b8d20(g2_layout2_slot_t *slot)
{
    const void *src;

    if (slot == NULL || slot->icon == NULL)
        return;
    if (slot->kind == 1u) {
        /* Kind 1 follows the live icon code in the dashboard state. */
        src = dashboard_icon_src_by_code_50f810(
            *(const uint16_t *)(const void *)&g2_dashboard_state[0x2a]);
        if (src != NULL)
            audio_uart_page_498680(slot->icon, src);
    } else {
        src = layout2_slot_icon_src_5b89f0(slot->kind);
        if (src != NULL)
            audio_uart_page_498680(slot->icon, src);
    }
}

void layout2_place_5b8e1a(void *obj, int32_t y)
{
    if (obj != NULL) {
        uint32_t o = (uint32_t)(uintptr_t)obj;
        audio_uart_page_43f6ac(o, layout2_align_from_setting_5b8e02(g2_layout2_align_setting));
        audio_uart_page_43f0e0(o, 0u);
        audio_uart_page_43f142(o, (uint32_t)y);
    }
}

/* Build slot `slot` (0..2): a transparent content-sized container holding a
 * 24x24 icon and a label to its right, then place it by slot row. */
void layout2_slot_create_5b8f18(uint32_t slot, uint8_t kind)
{
    g2_layout2_slot_t *rec;
    uint32_t cont, icon, label;
    char text[16];

    if (slot >= 3u || g2_layout2_parent == NULL)
        return;
    rec = &g2_layout2_slots[slot];
    rec->kind = kind;
    rec->active = 1u;
    rec->icon = NULL;
    rec->label = NULL;
    if (kind == 0u)
        return;

    cont = audio_uart_page_43de82((uint32_t)(uintptr_t)g2_layout2_parent);
    audio_uart_page_43f4c0(cont, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_44129e(cont, 0u, 0u);
    audio_uart_page_44131c(cont, 0u, 0u);
    audio_uart_page_44133a(cont, 0u, 0u);
    audio_uart_page_441386(cont, 0u, 0u);
    lv_obj_set_style_pad_all_5b8dd0(cont, 0u, 0u);
    audio_uart_page_44146a(cont, 0u, 0u);
    audio_uart_page_44140e(cont, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44142e(cont, 0xffu, 0u);
    audio_uart_page_43dfa4((void *)(uintptr_t)cont, LV_OBJ_FLAG_SCROLLABLE);
    g2_layout2_slot_conts[slot] = (void *)(uintptr_t)cont;

    icon = audio_uart_page_498668(cont);
    audio_uart_page_43f506(icon, 24u);
    audio_uart_page_43f568(icon, 24u);
    audio_uart_page_43f09a(icon, 0u, 0u);
    audio_uart_page_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_uart_page_43dfa4((void *)(uintptr_t)icon, LV_OBJ_FLAG_SCROLLABLE);
    rec->icon = (void *)(uintptr_t)icon;
    layout2_slot_icon_refresh_5b8d20(rec);

    label = audio_uart_page_499416(cont);
    audio_uart_page_43f506(label, LV_SIZE_CONTENT);
    audio_uart_page_43f568(label, LV_SIZE_CONTENT);
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
    rec->label = (void *)(uintptr_t)label;
    aeabi_memset_43c0e4(text, sizeof(text), 0);
    layout2_slot_text_5b8bc8(kind, text, sizeof(text));
    audio_uart_page_49942e((uint8_t *)(uintptr_t)label, text);
    audio_uart_page_43f6d6(label, icon, LV_ALIGN_OUT_RIGHT_MID, 8u, 0u);

    layout2_place_5b8e1a((void *)(uintptr_t)cont,
                         layout2_slot_y_5b8e4a(layout2_slot_row_5b8e5e(slot, g2_layout2_slot_count)));
}

void layout4_place_5bab76(void *obj, int32_t y)
{
    if (obj != NULL) {
        uint32_t o = (uint32_t)(uintptr_t)obj;
        audio_uart_page_43f6ac(o, layout4_align_from_setting_5bab5e(g2_layout4_align_setting));
        audio_uart_page_43f0e0(o, 0u);
        audio_uart_page_43f142(o, (uint32_t)y);
    }
}
