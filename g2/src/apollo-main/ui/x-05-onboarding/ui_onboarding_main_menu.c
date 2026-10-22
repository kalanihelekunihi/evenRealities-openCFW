/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_main_page.c
 * (page create code; the welcome/main views 0x4AAB90 and 0x4AB08C are in
 * ui/a-19-onboarding-main-create, the layout helper 0x4AB004 in
 * ui/u-02-onboarding). Written from the 2.2.6.10 disassembly (no inventory
 * rows, no Ghidra corpus entries):
 *   0x4AB6E4..0x4ABA49  ui_onboarding_menu_create_4ab6e4 (pad 0x4ABA4A, pool
 *                       0x4ABA4C..0x4ABA57 shared with a-19)
 *   0x4ABA58..0x4ABB99  ui_onboarding_main_create_4aba58
 *   0x4ABBA4..0x4ABBF3  ui_onboarding_main_destroy_4abba4
 * Literal pool words 0x4ABC6C..0x4ABCAF (and 0x4ABC00) belong to these
 * three functions. Compilation is not byte identity. */
#include <stdint.h>
#include <stddef.h>

#define LV_SIZE_CONTENT             0x3fffffff
#define LV_OBJ_FLAG_HIDDEN          0x1u
#define LV_OBJ_FLAG_CLICKABLE       0x2u
#define LV_OBJ_FLAG_SCROLLABLE      0x10u
#define LV_OBJ_FLAG_FLOATING        0x40000u
#define ONB_ALIGN_TOP_LEFT          1u
#define ONB_ALIGN_LEFT_MID          7u
#define ONB_ALIGN_OUT_BOTTOM_LEFT   13u
#define ONB_ALIGN_OUT_RIGHT_MID     20u
#define ONB_PAGE_WIDE               576 /* 0x240 */
#define ONB_PAGE_HEIGHT             288 /* 0x120 */
#define ONB_CARD_ICON_SIZE          24
#define ONB_CARD_ICON_PITCH         30
#define ONB_CARD_HIGHLIGHT_INDEX    4   /* Even AI card drawn at full opacity */
#define ONB_MENU_HINT_SPAN          547 /* 0x223: hint width = 547 - menu width */
#define ONB_ROLE_MASTER             1u

/* ROM 0x71aaac: feature cards of the onboarding side menu, 12 bytes each,
 * g2_onboarding_feature_card_count_200042b0 (= 5) entries. Defined in
 * onboarding_menu_data.c. */
typedef struct {
    const void *icon;      /* +0x00 lv_image_dsc_t */
    const char *text_key;  /* +0x04 i18n key */
    int32_t card_id;       /* +0x08 1..5 */
} g2_onboarding_feature_card_t;
_Static_assert(sizeof(g2_onboarding_feature_card_t) == 12u, "stock card stride");

extern const g2_onboarding_feature_card_t g2_onboarding_feature_cards_71aaac[]; /* ROM 0x71aaac */
extern int32_t g2_onboarding_feature_card_count_200042b0;  /* RAM 0x200042b0 (.data = 5) */

/* RAM state (defined in ui/S4-ui-a-data/onboarding_data.c unless noted). */
extern void *g2_onboarding_root_obj;                      /* RAM 0x20074834 */
extern void *g2_onboarding_event_fifo;                    /* RAM 0x20074cdc, ui_common byte FIFO */
extern int32_t g2_onboarding_feature_page_open;           /* RAM 0x20074ce4 */
extern void *g2_onboarding_main_obj_20074d60;             /* RAM 0x20074d60 onboarding_menu_container */
extern void *g2_onboarding_main_obj_20074d64;             /* RAM 0x20074d64 framed card list */
extern void *g2_onboarding_main_obj_20074d68;             /* RAM 0x20074d68 "access menu" hint label */
extern int32_t g2_onboarding_tile_index;                  /* RAM 0x20074d6c */
extern int32_t g2_onboarding_anim_busy;                   /* RAM 0x20074d7c */
extern int32_t g2_onboarding_main_flag_20074d88;          /* RAM 0x20074d88 */
extern uint8_t g2_onboarding_wait_peer_ack;               /* RAM 0x2007503d */
extern uint32_t audio_uart_ring_secondary_head_cell;      /* RAM 0x200746e0, current lv_font_t * */
/* Cells only this destroy path touches (defined in onboarding_menu_data.c). */
extern int32_t g2_onboarding_state_20074d74;              /* RAM 0x20074d74 */
extern int32_t g2_onboarding_state_20074d80;              /* RAM 0x20074d80 */
extern int32_t g2_onboarding_state_20074d84;              /* RAM 0x20074d84 */
extern int32_t g2_onboarding_state_20004290;              /* RAM 0x20004290 (.data = 200) */

/* LVGL 9.3 fork (names shared with ui/a-19-onboarding-main-create). */
extern void *audio_uart_page_43de82(void *parent);                      /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flags);          /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flags);          /* lv_obj_remove_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);    /* lv_obj_set_pos */
extern void audio_uart_page_43f506(void *obj, int32_t width);           /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t height);          /* lv_obj_set_height */
extern void audio_uart_page_43f66c(void *obj);                          /* lv_obj_update_layout */
extern void lv_obj_align_43f6b8(void *obj, uint8_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                          /* lv_obj_align_to */
extern int32_t audio_uart_lv_obj_width_43fd9e(void *obj);               /* lv_obj_get_width */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                   /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel); /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel); /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel); /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel); /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);   /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel); /* border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);      /* border_width */
extern void audio_uart_page_44133a(void *obj, int32_t v, uint32_t sel);      /* outline_width */
extern void audio_uart_page_441378(void *obj, int32_t v, uint32_t sel);      /* outline_pad */
extern void audio_uart_page_441386(void *obj, int32_t v, uint32_t sel);      /* shadow_width */
extern void audio_uart_page_441394(void *obj, int32_t v, uint32_t sel);      /* shadow_offset_x */
extern void audio_uart_page_4413a2(void *obj, int32_t v, uint32_t sel);      /* shadow_offset_y */
extern void audio_uart_page_4413b0(void *obj, int32_t v, uint32_t sel);      /* shadow_spread */
extern void audio_uart_page_4413ce(void *obj, uint32_t opa, uint32_t sel);   /* image_opa */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel); /* text_color */
extern void audio_uart_page_44142e(void *obj, uint32_t opa, uint32_t sel);   /* text_opa */
extern void audio_uart_page_44143e(void *obj, uint32_t font, uint32_t sel);  /* text_font */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);      /* radius */
extern void ui_onboarding_main_sub_004A856C(void *obj, int32_t v, uint32_t sel); /* lv_obj_set_style_pad_all copy */
extern void *audio_uart_page_498668(void *parent);                      /* lv_image_create */
extern void audio_uart_page_498680(void *image, const void *src);       /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                      /* lv_label_create */
extern const char *audio_uart_page_49942e(void *label, const char *text); /* lv_label_set_text */

/* Product helpers. */
extern uint32_t display_driver_uled_mode_45a568(void);                 /* device role, 1 = master */
extern uint32_t audio_uart_page_460084(const char *key);                /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */
extern void *heap_alloc_or_abort_51008a(uint32_t bytes);
extern void heap_free_51009c(void *block);
extern void *ui_common_api_fn_00509c1c(void);                           /* byte FIFO create */
extern void ui_common_api_fn_00509c96(void *fifo);                      /* byte FIFO destroy */
extern void onboarding_animation_deinit_50fbb6(void);

/* Page parts created by the other onboarding page units. */
extern void ui_onboarding_main_welcome_create_4aab90(void *parent);     /* a-19 */
extern void ui_onboarding_main_view_create_4ab08c(void *parent);        /* a-19 */
extern void ui_onboarding_main_touch_tips_create_4aae38(void *parent);  /* ui_onboarding_main_touch_tips.c */
extern void ui_onboarding_main_sub_004A9EDC(void);                      /* Onboarding_ProcessStart */
extern void ui_onboarding_main_sub_004A95E8(void *obj);

void ui_onboarding_menu_create_4ab6e4(void *parent);
void ui_onboarding_main_create_4aba58(void *display);
void ui_onboarding_main_destroy_4abba4(void);

static const char s_access_menu[] = "ID_ONBOARDING_ACCESS_MENU"; /* ROM 0x77418c */

#define ONB_TR(key) audio_uart_page_45fffe((key), audio_uart_page_460084(key))

/* Side menu shown during the feature step: a floating container holding a
 * white-framed list of icon + label rows (one per feature card, the Even AI
 * card at full opacity, the others dimmed) and, to its right, the hidden
 * "access menu" hint label. The left/right padding follows the device role
 * (master pads right). The per-card object arrays are scratch only. */
void ui_onboarding_menu_create_4ab6e4(void *parent)
{
    uint8_t role = (uint8_t)display_driver_uled_mode_45a568();
    void **icons;
    void **labels;
    int32_t hint_width;

    g2_onboarding_main_obj_20074d60 = audio_uart_page_43de82(parent);
    audio_uart_page_43f506(g2_onboarding_main_obj_20074d60, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_onboarding_main_obj_20074d60, ONB_PAGE_HEIGHT);
    audio_uart_page_43f09a(g2_onboarding_main_obj_20074d60, 0, 0);
    audio_uart_page_44127e(g2_onboarding_main_obj_20074d60, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_onboarding_main_obj_20074d60, 0xffu, 0u);
    audio_uart_page_44131c(g2_onboarding_main_obj_20074d60, 0, 0u);
    audio_uart_page_4412ec(g2_onboarding_main_obj_20074d60, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44146a(g2_onboarding_main_obj_20074d60, 0, 0u);
    ui_onboarding_main_sub_004A856C(g2_onboarding_main_obj_20074d60, 0, 0u);
    if (role == ONB_ROLE_MASTER)
        audio_uart_page_441238(g2_onboarding_main_obj_20074d60, 16, 0u);
    else
        audio_uart_page_44122a(g2_onboarding_main_obj_20074d60, 16, 0u);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074d60, LV_OBJ_FLAG_CLICKABLE);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d60, LV_OBJ_FLAG_FLOATING);

    g2_onboarding_main_obj_20074d64 = audio_uart_page_43de82(g2_onboarding_main_obj_20074d60);
    audio_uart_page_43f506(g2_onboarding_main_obj_20074d64, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_onboarding_main_obj_20074d64, ONB_PAGE_HEIGHT);
    audio_uart_page_43f09a(g2_onboarding_main_obj_20074d64, 0, 0);
    audio_uart_page_44127e(g2_onboarding_main_obj_20074d64, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_onboarding_main_obj_20074d64, 0xffu, 0u);
    audio_uart_page_44131c(g2_onboarding_main_obj_20074d64, 1, 0u);
    audio_uart_page_4412ec(g2_onboarding_main_obj_20074d64, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44146a(g2_onboarding_main_obj_20074d64, 6, 0u);
    audio_uart_page_44120e(g2_onboarding_main_obj_20074d64, 20, 0u);
    audio_uart_page_44121c(g2_onboarding_main_obj_20074d64, 20, 0u);
    audio_uart_page_441238(g2_onboarding_main_obj_20074d64, 24, 0u);
    audio_uart_page_44122a(g2_onboarding_main_obj_20074d64, 33, 0u);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074d64, LV_OBJ_FLAG_CLICKABLE);

    icons = heap_alloc_or_abort_51008a((uint32_t)g2_onboarding_feature_card_count_200042b0 * 4u);
    labels = heap_alloc_or_abort_51008a((uint32_t)g2_onboarding_feature_card_count_200042b0 * 4u);

    for (int32_t i = 0; i < g2_onboarding_feature_card_count_200042b0; i++) {
        const g2_onboarding_feature_card_t *card = &g2_onboarding_feature_cards_71aaac[i];

        icons[i] = audio_uart_page_498668(g2_onboarding_main_obj_20074d64);
        audio_uart_page_498680(icons[i], card->icon);
        audio_uart_page_43f506(icons[i], ONB_CARD_ICON_SIZE);
        audio_uart_page_43f568(icons[i], ONB_CARD_ICON_SIZE);
        audio_uart_page_44127e(icons[i], audio_uart_page_44104c(0x000000u), 0u);
        if (i == 0)
            lv_obj_align_43f6b8(icons[i], ONB_ALIGN_TOP_LEFT, 0, 3);
        else
            audio_uart_page_43f6d6(icons[i], icons[i - 1], ONB_ALIGN_OUT_BOTTOM_LEFT, 0,
                                   ONB_CARD_ICON_PITCH);

        labels[i] = audio_uart_page_499416(g2_onboarding_main_obj_20074d64);
        audio_uart_page_43f506(labels[i], LV_SIZE_CONTENT);
        audio_uart_page_43f568(labels[i], LV_SIZE_CONTENT);
        audio_uart_page_49942e(labels[i], ONB_TR(card->text_key));
        audio_uart_page_44143e(labels[i], audio_uart_ring_secondary_head_cell, 0u);
        audio_uart_page_43f6d6(labels[i], icons[i], ONB_ALIGN_OUT_RIGHT_MID, 8, 0);

        if (i == ONB_CARD_HIGHLIGHT_INDEX) {
            audio_uart_page_4413ce(icons[i], 0xffu, 0u);
            audio_uart_page_44140e(labels[i], audio_uart_page_44104c(0xffffffu), 0u);
        } else {
            audio_uart_page_4413ce(icons[i], 0x40u, 0u);
            audio_uart_page_44140e(labels[i], audio_uart_page_44104c(0x444444u), 0u);
        }
    }

    audio_uart_page_43f66c(g2_onboarding_main_obj_20074d60);
    hint_width = ONB_MENU_HINT_SPAN - audio_uart_lv_obj_width_43fd9e(g2_onboarding_main_obj_20074d60);

    g2_onboarding_main_obj_20074d68 = audio_uart_page_499416(parent);
    audio_uart_page_43f506(g2_onboarding_main_obj_20074d68, hint_width);
    audio_uart_page_43f568(g2_onboarding_main_obj_20074d68, LV_SIZE_CONTENT);
    lv_obj_align_43f6b8(g2_onboarding_main_obj_20074d68, ONB_ALIGN_LEFT_MID,
                        audio_uart_lv_obj_width_43fd9e(g2_onboarding_main_obj_20074d60) + 21, 0);
    audio_uart_page_44127e(g2_onboarding_main_obj_20074d68, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_onboarding_main_obj_20074d68, 0xffu, 0u);
    audio_uart_page_49942e(g2_onboarding_main_obj_20074d68, ONB_TR(s_access_menu));
    audio_uart_page_44140e(g2_onboarding_main_obj_20074d68, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(g2_onboarding_main_obj_20074d68, audio_uart_ring_secondary_head_cell, 0u);
    ui_onboarding_main_sub_004A856C(g2_onboarding_main_obj_20074d68, 12, 0u);
    if (role == ONB_ROLE_MASTER)
        audio_uart_page_441238(g2_onboarding_main_obj_20074d68, 16, 0u);
    else
        audio_uart_page_44122a(g2_onboarding_main_obj_20074d68, 16, 0u);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d68, LV_OBJ_FLAG_HIDDEN);

    heap_free_51009c(labels);
    heap_free_51009c(icons);
}

/* Onboarding page create (called by the onboarding app with the display
 * root): event FIFO, plain 576x288 black page root, then the welcome, main,
 * menu and touch-tips views, a layout pass and Onboarding_ProcessStart. */
void ui_onboarding_main_create_4aba58(void *display)
{
    if (g2_onboarding_event_fifo == NULL)
        g2_onboarding_event_fifo = ui_common_api_fn_00509c1c();
    g2_onboarding_anim_busy = 0;

    g2_onboarding_root_obj = audio_uart_page_43de82(display);
    audio_uart_page_43dfa4(g2_onboarding_root_obj, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_43f506(g2_onboarding_root_obj, ONB_PAGE_WIDE);
    audio_uart_page_43f568(g2_onboarding_root_obj, ONB_PAGE_HEIGHT);
    audio_uart_page_43f09a(g2_onboarding_root_obj, 0, 0);
    audio_uart_page_43dfa4(g2_onboarding_root_obj, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_44127e(g2_onboarding_root_obj, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_onboarding_root_obj, 0xffu, 0u);
    audio_uart_page_44140e(g2_onboarding_root_obj, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44142e(g2_onboarding_root_obj, 0xffu, 0u);
    audio_uart_page_4412ec(g2_onboarding_root_obj, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44131c(g2_onboarding_root_obj, 0, 0u);
    audio_uart_page_44133a(g2_onboarding_root_obj, 0, 0u);
    audio_uart_page_441378(g2_onboarding_root_obj, 0, 0u);
    audio_uart_page_441386(g2_onboarding_root_obj, 0, 0u);
    audio_uart_page_4413b0(g2_onboarding_root_obj, 0, 0u);
    audio_uart_page_441394(g2_onboarding_root_obj, 0, 0u);
    audio_uart_page_4413a2(g2_onboarding_root_obj, 0, 0u);
    audio_uart_page_44146a(g2_onboarding_root_obj, 0, 0u);
    ui_onboarding_main_sub_004A856C(g2_onboarding_root_obj, 0, 0u);
    audio_uart_page_44120e(g2_onboarding_root_obj, 0, 0u);
    audio_uart_page_44121c(g2_onboarding_root_obj, 0, 0u);
    audio_uart_page_44122a(g2_onboarding_root_obj, 0, 0u);
    audio_uart_page_441238(g2_onboarding_root_obj, 0, 0u);

    ui_onboarding_main_welcome_create_4aab90(g2_onboarding_root_obj);
    ui_onboarding_main_view_create_4ab08c(g2_onboarding_root_obj);
    ui_onboarding_menu_create_4ab6e4(g2_onboarding_root_obj);
    ui_onboarding_main_touch_tips_create_4aae38(g2_onboarding_root_obj);
    audio_uart_page_43f66c(g2_onboarding_root_obj);
    ui_onboarding_main_sub_004A9EDC();
    ui_onboarding_main_sub_004A95E8(g2_onboarding_root_obj);
}

/* Onboarding page destroy: resets the page state cells (0x20004290 back to
 * its .data value 200), tears down the tutorial animation and frees the
 * event FIFO (UI registry exit event 5, ui/a-10-onboarding). It deletes no
 * LVGL object itself. */
void ui_onboarding_main_destroy_4abba4(void)
{
    g2_onboarding_tile_index = 0;
    g2_onboarding_state_20074d74 = 0;
    g2_onboarding_anim_busy = 0;
    g2_onboarding_feature_page_open = 0;
    g2_onboarding_main_flag_20074d88 = 0;
    g2_onboarding_state_20074d80 = 0;
    g2_onboarding_state_20074d84 = 0;
    g2_onboarding_state_20004290 = 200;
    g2_onboarding_wait_peer_ack = 0u;
    onboarding_animation_deinit_50fbb6();
    if (g2_onboarding_event_fifo != NULL) {
        ui_common_api_fn_00509c96(g2_onboarding_event_fifo);
        g2_onboarding_event_fifo = NULL;
    }
}
