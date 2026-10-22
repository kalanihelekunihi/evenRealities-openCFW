/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\MessageNotify\ui_msg_notif_list.c
 * Native 0x551ed8..0x552856 (message_notify_ui_reflash, message_notify_page_init,
 * page deinit); literal pools 0x552218..0x55225b and 0x552858..0x5528b7.
 *
 * The list is a vertical LVGL tileview of 214 px tiles with three recycled item
 * records (window of 3 messages around the selection) and a 10-dot page
 * indicator on the left edge. MSG_NOTIF_MAX_NUM is 10. */
#include <stdint.h>
#include <stddef.h>

enum { MSG_NOTIF_MAX_NUM = 10u, MSG_NOTIF_ITEM_SLOTS = 3u, MSG_NOTIF_TILE_H = 0xd6 };

enum {
    REFLASH_KEEP_SELECTION = 0u, /* refresh, keep index, scroll to it */
    REFLASH_NEW_MESSAGE = 1u,    /* reset to the newest message */
    REFLASH_CLAMP = 2u,          /* after deletion, clamp index */
    REFLASH_SCROLL_ONLY = 3u,
};

enum {
    LV_OBJ_FLAG_HIDDEN = 0x1u,
    LV_OBJ_FLAG_SCROLLABLE = 0x10u,
    LV_ALIGN_TOP_LEFT = 1u,
    LV_ALIGN_TOP_MID = 2u,
    LV_ALIGN_LEFT_MID = 7u,
    LV_ALIGN_CENTER = 9u,
    LV_ALIGN_OUT_BOTTOM_LEFT = 0x0du,
    LV_DIR_VER = 0x0cu,
    LV_SIZE_CONTENT = 0x3fffffff,
};

/* One list tile record, 0x28 bytes (msg_notif_create_msg_item 0x551814). */
typedef struct {
    void *tile;              /* +0x00 tileview tile */
    uint8_t reserved_04[0x24];
} g2_msg_notif_item_t;
_Static_assert(sizeof(g2_msg_notif_item_t) == 0x28, "stock item stride");

/* List UI context (RAM 0x2006f734, cleared with 0x1d0 bytes at init); same
 * layout as in ui/a-52-msg-notif-list. Only items[0..2] are created. */
typedef struct {
    void *root;                           /* +0x00 576x214 container */
    void *empty_text;                     /* +0x04 "ID_NOTIFICATIONS_EMPTY" label */
    void *empty_label;                    /* +0x08 bordered empty-state box */
    void *indicator;                      /* +0x0c 4x28 dot column viewport */
    void *dots[MSG_NOTIF_MAX_NUM];        /* +0x10 */
    void *indicator_edge;                 /* +0x38 */
    void *tileview;                       /* +0x3c */
    g2_msg_notif_item_t items[MSG_NOTIF_MAX_NUM]; /* +0x40 */
} g2_msg_notif_ui_t;
_Static_assert(offsetof(g2_msg_notif_ui_t, tileview) == 0x3c, "tileview at +0x3c");
_Static_assert(offsetof(g2_msg_notif_ui_t, items) == 0x40, "items at +0x40");
_Static_assert(sizeof(g2_msg_notif_ui_t) == 0x1d0, "stock memset size");

extern g2_msg_notif_ui_t g2_msg_notif_ui_2006f734;              /* RAM 0x2006f734 */
extern int32_t g2_msg_notif_current_index_20074cd0;             /* RAM 0x20074cd0 selected message index */
extern uint8_t g2_msg_notif_anim_busy;                          /* RAM 0x2007503c */
extern void *g2_msg_notif_event_fifo;                           /* RAM 0x20074cd8 */
extern int8_t g2_msg_notif_delete_tile_20004554;                /* RAM 0x20004554, -1 none */
extern int8_t g2_msg_notif_delete_count_20004555;               /* RAM 0x20004555 */
extern int8_t g2_msg_notif_delete_visible_20004556;             /* RAM 0x20004556 */
extern uint32_t audio_system_alert_font_200746e0;               /* RAM 0x200746e0 lv_font_t * */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *ui_common_api_fn_00509c1c(void);                /* fifo create */
extern void ui_common_api_fn_00509c96(void *fifo);           /* fifo destroy */
extern uint32_t audio_settings_unread_message_count(void);   /* service_ancc_message_count_get 0x4974d4 */
extern uint32_t display_driver_uled_mode_45a568(void);       /* device role, 1 master */

extern void msg_tile_binding_init_54ff36(void);
extern void msg_tile_binding_clear_54ff48(void);
extern void lv_obj_set_style_pad_all_54fa24(void *obj, int32_t value, uint32_t selector);
extern g2_msg_notif_item_t *msg_notif_create_msg_item_551814(void *tileview, uint8_t index, g2_msg_notif_item_t *item);
extern void msg_notif_fill_msg_item_551abc(g2_msg_notif_item_t *item, uint8_t msg_index, uint8_t tile_index);
extern void msg_notif_refresh_visibility_551e5c(void);
extern int16_t msg_tile_index_find_by_msg_index_550170(uint8_t msg_index); /* -1 when not bound */
extern void msg_notif_jump_to_message_absolute_550968(uint32_t index);

extern void *audio_uart_page_43de82(void *parent);                              /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);                   /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                   /* lv_obj_remove_flag */
extern void audio_uart_page_43f506(void *obj, int32_t w);                       /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                       /* lv_obj_set_height */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);                       /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);                       /* lv_obj_set_y */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x, int32_t y); /* lv_obj_align_to */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);                   /* lv_obj_set_scrollbar_mode */
extern void audio_uart_page_44e3ca(void *obj, uint32_t dir);                    /* lv_obj_set_scroll_dir */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                           /* lv_color_hex */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel);    /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);      /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel);    /* border_color */
extern void audio_uart_page_44130c(void *obj, uint32_t opa, uint32_t sel);      /* border_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);         /* border_width */
extern void audio_uart_page_44133a(void *obj, int32_t v, uint32_t sel);         /* outline_width */
extern void lv_obj_set_style_outline_color_441348(void *obj, uint32_t color, uint32_t sel);
extern void lv_obj_set_style_outline_opa_441368(void *obj, uint32_t opa, uint32_t sel);
extern void audio_uart_page_441378(void *obj, int32_t v, uint32_t sel);         /* outline_pad */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel);    /* text_color */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel);  /* text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t sel);    /* text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);         /* radius */
extern void *audio_uart_page_499416(void *parent);                              /* lv_label_create */
extern void audio_uart_page_49942e(void *label, const char *text);              /* lv_label_set_text */
extern void *lv_tileview_create_50fef8(void *parent);
extern uint32_t audio_uart_page_460084(const char *key);                        /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);     /* localized text */

static const char module_tag[] = "message_notify_list.ui"; /* ROM 0x77d36c */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\MessageNotify\\ui_msg_notif_list.c"; /* ROM 0x6f0ad8 */
static const char fn_reflash[] = "message_notify_ui_reflash"; /* ROM 0x774100 */
static const char fn_page_init[] = "message_notify_page_init"; /* ROM 0x77411c */
static const char fifo_fail[] = "failed to create FIFO instance"; /* ROM 0x7676f0 */
static const char fifo_fail_short[] = "[message_notify_list.ui]failed to create FIFO instance"; /* ROM 0x7255d8 */
static const char root_null[] = "root_obj is NULL"; /* ROM 0x784860 */
static const char root_null_short[] = "[message_notify_list.ui]root_obj is NULL"; /* ROM 0x745f8c */
static const char tileview_null[] = "tileview is NULL"; /* ROM 0x784874 */
static const char tileview_null_short[] = "[message_notify_list.ui]tileview is NULL"; /* ROM 0x745fb8 */
static const char count_limit[] = "msg_notif_count (%d) exceeds MSG_NOTIF_MAX_NUM (%d), limiting to max"; /* ROM 0x6feb7c */
static const char count_limit_short[] = "[message_notify_list.ui]msg_notif_count (%d) exceeds MSG_NOTIF_MAX_NUM (%d), limiting to max"; /* ROM 0x6dedf4 */
static const char item_fail[] = "failed to create message item %d"; /* ROM 0x75c54c */
static const char item_fail_short[] = "[message_notify_list.ui]failed to create message item %d"; /* ROM 0x71aa70 */
static const char empty_key[] = "ID_NOTIFICATIONS_EMPTY"; /* ROM 0x77d3e4 */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

static void ensure_event_fifo(const char *fn, uint32_t line)
{
    if (g2_msg_notif_event_fifo != NULL)
        return;
    g2_msg_notif_event_fifo = ui_common_api_fn_00509c1c();
    if (g2_msg_notif_event_fifo != NULL)
        return;
    if (log_extended_on())
        audio_log_extended(1u, module_tag, source_file, fn, line, fifo_fail);
    if (log_compressed_on())
        (void)compress_log_output(0x04000000u, fifo_fail_short, fifo_fail_short);
}

static void scroll_to_selected(g2_msg_notif_ui_t *ui)
{
    int16_t tile = msg_tile_index_find_by_msg_index_550170((uint8_t)g2_msg_notif_current_index_20074cd0);
    if (tile >= 0)
        audio_uart_lv_scroll_to_y_44ea04(ui->tileview, (int16_t)(tile * MSG_NOTIF_TILE_H), 0u);
}

/* Rebinds the three item slots to the messages around the selection and
 * scrolls the tileview to the selected one. */
void message_notify_ui_reflash_551ed8(void *page, uint8_t mode)
{
    g2_msg_notif_ui_t *ui = &g2_msg_notif_ui_2006f734;

    ensure_event_fifo(fn_reflash, 0x7e9u);
    if (page == NULL) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_reflash, 0x7f0u, root_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, root_null_short, root_null_short);
        return;
    }
    if (ui->tileview == NULL) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_reflash, 0x7f6u, tileview_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, tileview_null_short, tileview_null_short);
        return;
    }

    uint8_t count = (uint8_t)audio_settings_unread_message_count();
    if (count > MSG_NOTIF_MAX_NUM) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_reflash, 0x800u, count_limit, count,
                               MSG_NOTIF_MAX_NUM);
        if (log_compressed_on())
            (void)compress_log_output(0x08800000u, count_limit_short, count_limit_short, count,
                                      MSG_NOTIF_MAX_NUM);
        count = MSG_NOTIF_MAX_NUM;
    }
    msg_tile_binding_clear_54ff48();

    if (mode == REFLASH_KEEP_SELECTION) {
        if (count != 0u)
            g2_msg_notif_current_index_20074cd0 = 0;
    } else if (mode == REFLASH_NEW_MESSAGE) {
        g2_msg_notif_current_index_20074cd0 = 0;
    } else if (mode == REFLASH_CLAMP) {
        if (count == 0u)
            g2_msg_notif_current_index_20074cd0 = 0;
        else if (g2_msg_notif_current_index_20074cd0 >= (int32_t)count)
            g2_msg_notif_current_index_20074cd0 = (int32_t)count - 1;
    }

    if (count != 0u) {
        if (g2_msg_notif_current_index_20074cd0 >= (int32_t)count)
            g2_msg_notif_current_index_20074cd0 = (int32_t)count - 1;
        uint8_t slot = 0u;
        for (uint32_t i = 0u; (uint8_t)i < MSG_NOTIF_ITEM_SLOTS; i++) {
            /* window starts one before the selection, two before at the end */
            int32_t back = (g2_msg_notif_current_index_20074cd0 < (int32_t)count - 1) ? 1 : 2;
            uint32_t index = i + (uint32_t)g2_msg_notif_current_index_20074cd0 - (uint32_t)back;
            int8_t signed_index = (int8_t)index;
            if (signed_index >= 0 && (int16_t)signed_index < (int16_t)count) {
                msg_notif_fill_msg_item_551abc(&ui->items[slot], (uint8_t)index, slot);
                slot++;
            }
        }
        for (; slot < MSG_NOTIF_ITEM_SLOTS; slot++)
            audio_uart_page_43ded4(ui->items[slot].tile, LV_OBJ_FLAG_HIDDEN);
    }
    msg_notif_refresh_visibility_551e5c();

    if (mode == REFLASH_KEEP_SELECTION) {
        if (count != 0u)
            scroll_to_selected(ui);
    } else if (mode == REFLASH_NEW_MESSAGE) {
        if (g2_msg_notif_current_index_20074cd0 == 0 && count >= 2u) {
            g2_msg_notif_current_index_20074cd0++;
            scroll_to_selected(ui);
        }
        msg_notif_jump_to_message_absolute_550968(0u);
    } else if (mode == REFLASH_CLAMP) {
        if (count != 0u)
            scroll_to_selected(ui);
    } else if (mode == REFLASH_SCROLL_ONLY) {
        if (count != 0u)
            scroll_to_selected(ui);
    }
}

void message_notify_page_init_55225c(void *page)
{
    g2_msg_notif_ui_t *ui = &g2_msg_notif_ui_2006f734;

    if (page == NULL) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_page_init, 0x87eu, root_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, root_null_short, root_null_short);
        return;
    }
    ensure_event_fifo(fn_page_init, 0x886u);
    g2_msg_notif_anim_busy = 0u;
    (void)aeabi_memset_43c0e4(ui, sizeof(*ui), 0);
    msg_tile_binding_init_54ff36();

    audio_uart_page_43f506(page, 0x240);
    audio_uart_page_43f568(page, 0x120);
    audio_uart_page_43f0e0(page, 0);
    audio_uart_page_43f142(page, 0);
    audio_uart_page_43ded4(page, 0x50000u);
    audio_uart_page_43dfa4(page, 0xb014u);
    audio_uart_page_44e368(page, 0u);
    audio_uart_page_44146a(page, 0, 0u);
    audio_uart_page_44127e(page, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(page, 0u, 0u);
    audio_uart_page_44131c(page, 0, 0u);
    lv_obj_set_style_pad_all_54fa24(page, 0, 0u);

    ui->root = audio_uart_page_43de82(page);
    audio_uart_page_43f506(ui->root, 0x240);
    audio_uart_page_43f568(ui->root, MSG_NOTIF_TILE_H);
    audio_uart_page_43f6b8(ui->root, LV_ALIGN_TOP_LEFT, 0, -16);
    audio_uart_page_44131c(ui->root, 0, 0u);
    audio_uart_page_44127e(ui->root, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(ui->root, 0xffu, 0u);
    audio_uart_page_44146a(ui->root, 0, 0u);
    lv_obj_set_style_pad_all_54fa24(ui->root, 0, 0u);
    audio_uart_page_43dfa4(ui->root, 0x12u);

    /* the master eye shifts the column 16 px further left */
    int16_t x_shift = 8;
    if ((uint8_t)display_driver_uled_mode_45a568() == 1u)
        x_shift = -8;

    ui->indicator = audio_uart_page_43de82(ui->root);
    audio_uart_page_43f506(ui->indicator, 4);
    audio_uart_page_43f568(ui->indicator, 0x1c);
    audio_uart_page_43f6b8(ui->indicator, LV_ALIGN_LEFT_MID, (int16_t)(x_shift + 8), 0x10);
    audio_uart_page_44127e(ui->indicator, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(ui->indicator, 0xffu, 0u);
    audio_uart_page_44131c(ui->indicator, 0, 0u);
    audio_uart_page_44146a(ui->indicator, 0, 0u);
    lv_obj_set_style_pad_all_54fa24(ui->indicator, 0, 0u);
    audio_uart_page_43ded4(ui->indicator, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_44e368(ui->indicator, 0u);
    audio_uart_page_44e3ca(ui->indicator, LV_DIR_VER);
    audio_uart_page_43ded4(ui->indicator, LV_OBJ_FLAG_HIDDEN);

    for (uint8_t i = 0u; i < MSG_NOTIF_MAX_NUM; i++) {
        ui->dots[i] = audio_uart_page_43de82(ui->indicator);
        audio_uart_page_43f506(ui->dots[i], 4);
        audio_uart_page_43f568(ui->dots[i], 4);
        audio_uart_page_43f6b8(ui->dots[i], LV_ALIGN_OUT_BOTTOM_LEFT, 0, (int32_t)i * 0xc);
        audio_uart_page_44127e(ui->dots[i], audio_uart_page_44104c(0x444444u), 0u);
        audio_uart_page_44129e(ui->dots[i], 0xffu, 0u);
        audio_uart_page_44131c(ui->dots[i], 0, 0u);
        audio_uart_page_44146a(ui->dots[i], 0, 0u);
        lv_obj_set_style_pad_all_54fa24(ui->dots[i], 0, 0u);
        audio_uart_page_43dfa4(ui->dots[i], 0x12u);
    }

    ui->indicator_edge = audio_uart_page_43de82(ui->root);
    audio_uart_page_43f506(ui->indicator_edge, 4);
    audio_uart_page_43f568(ui->indicator_edge, 4);
    audio_uart_page_43f6d6(ui->indicator_edge, ui->indicator, LV_ALIGN_TOP_LEFT, 0, 0);
    audio_uart_page_44127e(ui->indicator_edge, audio_uart_page_44104c(0x444444u), 0u);
    audio_uart_page_44129e(ui->indicator_edge, 0xffu, 0u);
    audio_uart_page_44131c(ui->indicator_edge, 0, 0u);
    audio_uart_page_44146a(ui->indicator_edge, 0, 0u);
    lv_obj_set_style_pad_all_54fa24(ui->indicator_edge, 0, 0u);
    audio_uart_page_43dfa4(ui->indicator_edge, 0x12u);
    audio_uart_page_43ded4(ui->indicator_edge, LV_OBJ_FLAG_HIDDEN);

    ui->empty_label = audio_uart_page_43de82(ui->root);
    audio_uart_page_43f506(ui->empty_label, 0x224);
    audio_uart_page_43f568(ui->empty_label, 0xc6);
    audio_uart_page_43f6b8(ui->empty_label, LV_ALIGN_TOP_MID, (int16_t)(x_shift + 6), 0x10);
    audio_uart_page_44127e(ui->empty_label, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(ui->empty_label, 0xffu, 0u);
    audio_uart_page_44131c(ui->empty_label, 1, 0u);
    audio_uart_page_4412ec(ui->empty_label, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44130c(ui->empty_label, 0xffu, 0u);
    audio_uart_page_44146a(ui->empty_label, 6, 0u);
    lv_obj_set_style_pad_all_54fa24(ui->empty_label, 0, 0u);
    audio_uart_page_43dfa4(ui->empty_label, 0x12u);

    ui->empty_text = audio_uart_page_499416(ui->empty_label);
    audio_uart_page_43f506(ui->empty_text, 0x224);
    audio_uart_page_43f568(ui->empty_text, LV_SIZE_CONTENT);
    audio_uart_page_43f6b8(ui->empty_text, LV_ALIGN_CENTER, 0, 0);
    audio_uart_page_49942e(ui->empty_text,
                           audio_uart_page_45fffe(empty_key, audio_uart_page_460084(empty_key)));
    audio_uart_page_44145a(ui->empty_text, 2u, 0u);
    audio_uart_page_44140e(ui->empty_text, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(ui->empty_text, (const void *)(uintptr_t)audio_system_alert_font_200746e0, 0u);
    audio_uart_page_44127e(ui->empty_text, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(ui->empty_text, 0xffu, 0u);
    audio_uart_page_44131c(ui->empty_text, 0, 0u);
    lv_obj_set_style_pad_all_54fa24(ui->empty_text, 0, 0u);
    audio_uart_page_43dfa4(ui->empty_text, 0x12u);

    ui->tileview = lv_tileview_create_50fef8(ui->root);
    audio_uart_page_43f506(ui->tileview, 0x224);
    audio_uart_page_43f568(ui->tileview, MSG_NOTIF_TILE_H);
    audio_uart_page_43f6b8(ui->tileview, LV_ALIGN_CENTER, (int16_t)(x_shift + 6), 0);
    audio_uart_page_44127e(ui->tileview, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(ui->tileview, 0xffu, 0u);
    lv_obj_set_style_pad_all_54fa24(ui->tileview, 0, 0u);
    audio_uart_page_44146a(ui->tileview, 0, 0u);
    lv_obj_set_style_outline_color_441348(ui->tileview, audio_uart_page_44104c(0u), 0u);
    lv_obj_set_style_outline_opa_441368(ui->tileview, 0xffu, 0u);
    audio_uart_page_44133a(ui->tileview, 0, 0u);
    audio_uart_page_441378(ui->tileview, 0, 0u);
    audio_uart_page_43ded4(ui->tileview, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_44e368(ui->tileview, 0u);
    audio_uart_page_44e3ca(ui->tileview, LV_DIR_VER);

    for (uint8_t i = 0u; i < MSG_NOTIF_ITEM_SLOTS; i++) {
        if (msg_notif_create_msg_item_551814(ui->tileview, i, &ui->items[i]) == NULL) {
            if (log_extended_on())
                audio_log_extended(1u, module_tag, source_file, fn_page_init, 0x911u, item_fail, i);
            if (log_compressed_on())
                (void)compress_log_output(0x04400000u, item_fail_short, item_fail_short, i);
        } else {
            audio_uart_page_43ded4(ui->items[i].tile, LV_OBJ_FLAG_HIDDEN);
        }
    }
    message_notify_ui_reflash_551ed8(page, REFLASH_KEEP_SELECTION);
}

void message_notify_page_deinit_552820(void)
{
    g2_msg_notif_current_index_20074cd0 = 0;
    g2_msg_notif_anim_busy = 0u;
    if (g2_msg_notif_event_fifo != NULL) {
        ui_common_api_fn_00509c96(g2_msg_notif_event_fifo);
        g2_msg_notif_event_fifo = NULL;
    }
    msg_tile_binding_clear_54ff48();
    g2_msg_notif_delete_tile_20004554 = -1;
    g2_msg_notif_delete_count_20004555 = -1;
    g2_msg_notif_delete_visible_20004556 = -1;
}
