/* Onboarding news page, scrolling part (second half of the TU), stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_news_page.c
 * (log tag "onboarding.news"). Native 0x50bd1c..0x50bf95, 0x50bfb0..0x50c13f,
 * 0x50c150..0x50c1bb, 0x50c1c0..0x50c27b, 0x50c288..0x50c2ed, 0x50c314..0x50c3e7,
 * 0x50c3f4..0x50c4a1, 0x50c4ac..0x50c519, 0x50c528..0x50c645, 0x50c654..0x50c6b5,
 * 0x50c6cc..0x50c761, 0x50c768..0x50c7a1, 0x50c7a8..0x50c861, 0x50c868..0x50c95d;
 * literal pools 0x50bf98..0x50bfaf, 0x50c140..0x50c14f, 0x50c1bc, 0x50c27c..0x50c287,
 * 0x50c2f0..0x50c313, 0x50c4a4..0x50c4ab, 0x50c51c..0x50c527, 0x50c648..0x50c653,
 * 0x50c6b8..0x50c6cb, 0x50c764, 0x50c7a4 (inline ""), 0x50c864 and
 * 0x50c960..0x50ca23. The first half (page create, key handling, FIFO,
 * load_news_data 0x50b438, update_content_state 0x50b5f4, vertical scroll
 * 0x50b744, switch_to_next_news 0x50ba64) is reconstructed separately.
 *
 * The page shows one news item at a time in a carousel of four 0x30-byte
 * containers (RAM 0x20071048) sitting at y = -288, 0, 288 and 576 inside the
 * page; a switch moves all four by one slot with a 400 ms container animation
 * and recycles the container that leaves the window. News items come from a
 * mutex-protected FIFO (peek / pop wrappers 0x50b19a / 0x50b18c, count
 * 0x50b1ac; the peeked record lands in RAM 0x20061110). Input that arrives
 * while an animation runs is queued as 7-byte key records in the ext fifo and
 * replayed from the animation completion callbacks.
 *
 * 0x50bfb0, 0x50c150 and 0x50c768 are lv_anim callbacks that the function
 * inventory does not list; they are reconstructed here with descriptive names. */
#include <stdint.h>
#include <stddef.h>

#define NEWS_CONTAINERS 4
#define NEWS_SLOT_H 288          /* 0x120 */
#define NEWS_POS_PREV (-288)     /* ROM 0x50c864 */
#define NEWS_POS_CUR 0
#define NEWS_POS_NEXT 288
#define NEWS_POS_NEXT2 576       /* 0x240 */
#define NEWS_SWITCH_ANIM_MS 400
#define LV_SCROLLBAR_MODE_OFF 0u
#define LV_SCROLLBAR_MODE_AUTO 3u
#define WAIT_FOREVER 0xffffffffu

/* lv_anim_t (LVGL 9.3 fork) as laid out on the stock 0x60-byte frame. */
typedef struct {
    void *var;                          /* +0x00 */
    void (*exec_cb)(void *, int32_t);   /* +0x04 */
    void *custom_exec_cb;               /* +0x08 */
    void *start_cb;                     /* +0x0c */
    void (*completed_cb)(void *);       /* +0x10 */
    void *deleted_cb;                   /* +0x14 */
    void *get_value_cb;                 /* +0x18 */
    void *user_data;                    /* +0x1c */
    int32_t (*path_cb)(const void *);   /* +0x20 */
    int32_t start_value;                /* +0x24 */
    int32_t current_value;              /* +0x28 */
    int32_t end_value;                  /* +0x2c */
    int32_t duration;                   /* +0x30 */
    uint8_t rest[0x2c];                 /* +0x34 */
} g2_lv_anim_t;
_Static_assert(sizeof(g2_lv_anim_t) == 0x60, "stock anim frame is 96 bytes");

/* One carousel slot. */
typedef struct {
    void *root;               /* +0x00 container object, moved by lv_obj_set_y */
    void *content_scroll;     /* +0x04 vertically scrolling content */
    void *obj_08;             /* +0x08 */
    void *source_label;       /* +0x0c */
    void *time_label;         /* +0x10 */
    void *title_label;        /* +0x14 */
    void *content_label;      /* +0x18 */
    uint32_t news_id;         /* +0x1c id of the loaded FIFO record */
    int32_t position_y;       /* +0x20 -288 / 0 / 288 / 576 */
    uint8_t scrollable;       /* +0x24 content taller than the viewport */
    uint8_t at_top;           /* +0x25 */
    uint8_t at_bottom;        /* +0x26 */
    uint8_t flag_27;          /* +0x27 */
    uint8_t flag_28;          /* +0x28 */
    uint8_t data_loaded;      /* +0x29 */
    uint8_t reserved_2a[2];
    int32_t read_count;       /* +0x2c */
} g2_onboarding_news_container_t;
_Static_assert(sizeof(g2_onboarding_news_container_t) == 0x30, "news container");

/* RAM 0x20071048. */
typedef struct {
    g2_onboarding_news_container_t container[NEWS_CONTAINERS]; /* +0x00 */
    int32_t news_count;       /* +0xc0 FIFO count, refreshed by sync_count */
    uint8_t is_switching;     /* +0xc4 container switch animation running */
    uint8_t reserved_c5[3];
    void *page_obj;           /* +0xc8 */
} g2_onboarding_news_scroll_t;

/* RAM 0x20073c80: target slots applied when the switch animation completes. */
typedef struct {
    int32_t direction;        /* +0x00 -1 previous */
    int32_t target_y[NEWS_CONTAINERS]; /* +0x04 */
    uint8_t pending;          /* +0x14 */
} g2_onboarding_news_pending_t;

/* FIFO record buffer filled by the peek/pop wrappers (RAM 0x20061110);
 * only the id is used here. */
typedef struct {
    uint32_t id;              /* +0x00 */
} g2_onboarding_news_record_t;

/* Key sync record decoded by ui_onboarding_main_sub_004A979C. */
typedef struct {
    uint8_t key;
    uint8_t process_id;
    uint8_t substep;
    uint8_t reserved;
    uint32_t value;
} g2_onboarding_key_msg_t;
_Static_assert(sizeof(g2_onboarding_key_msg_t) == 8u, "key sync record");

/* RAM state. The ui_onboarding_main_page.c names for 0x20071048 / 0x20074db8
 * are reused; both belong to this news page. */
extern g2_onboarding_news_scroll_t g2_onboarding_stock_page_20071048; /* RAM 0x20071048 */
extern int32_t g2_onboarding_stock_flag_20074db8;    /* RAM 0x20074db8 news ext page open (1) */
extern void *g2_onboarding_news_ext_fifo_20074db0;    /* RAM 0x20074db0 queued key records */
extern void *g2_onboarding_mutex;                     /* RAM 0x20074830 osMutexId_t */
extern g2_onboarding_news_record_t g2_onboarding_news_record_20061110; /* RAM 0x20061110 */
extern int32_t g2_onboarding_news_animating_20074d94; /* RAM 0x20074d94 */
extern uint8_t g2_onboarding_news_anim_kind_2007503e; /* RAM 0x2007503e 0 none, 1 content, 2 switch */
extern void *g2_onboarding_news_anim_obj_20074d8c;    /* RAM 0x20074d8c content anim target */
extern g2_onboarding_news_pending_t g2_onboarding_news_pending_20073c80; /* RAM 0x20073c80 */
extern int32_t g2_onboarding_news_start_y_20073f14[NEWS_CONTAINERS];     /* RAM 0x20073f14 */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* RTOS, libc. */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout); /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                   /* 0x44981c */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);

/* LVGL 9 (stock copies). */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(const void *obj);   /* lv_obj_is_valid */
extern void audio_uart_page_43f142(void *obj, int32_t y);                 /* lv_obj_set_y */
extern void audio_uart_page_43f66c(void *obj);                            /* lv_obj_update_layout */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);                     /* lv_obj_get_y */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);             /* lv_obj_set_scrollbar_mode */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                     /* lv_obj_get_scroll_y */
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *obj);             /* lv_obj_get_scroll_bottom */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *a);
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *a, int32_t start, int32_t end);
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *a);
extern int32_t audio_uart_lv_anim_path_450672(const void *a);             /* lv_anim_path_ease_out */
extern void audio_uart_page_49942e(void *label, const char *text);       /* lv_label_set_text */

/* ui_common byte FIFO, onboarding main page. */
extern int32_t ui_common_api_fn_00509dfa(void *fifo);                     /* 1 empty, 0 has data */
extern int32_t ui_common_api_fn_00509e14(void *fifo, void *data, uint32_t len); /* pop */
extern int32_t ui_onboarding_main_sub_004A979C(const uint8_t *raw, int32_t offset,
                                               g2_onboarding_key_msg_t *out);

/* First half of this TU. */
extern void onboarding_news_ext_input_event_warpper_50a670(uint8_t key, uint32_t value);
extern uint8_t onboarding_news_fifo_pop_50b18c(g2_onboarding_news_record_t *out);
extern uint8_t onboarding_news_fifo_peek_50b19a(g2_onboarding_news_record_t *out, uint16_t index);
extern uint16_t onboarding_news_fifo_count_50b1ac(void);
extern void onboarding_news_scroll_load_news_data_50b438(g2_onboarding_news_container_t *c, int32_t index);
extern void onboarding_news_scroll_update_content_state_50b5f4(g2_onboarding_news_container_t *c);

static const char module_tag[] = "onboarding.news"; /* ROM 0x789df0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\onboarding\\ui_onboarding_news_page.c"; /* ROM 0x6eab04 */
static const char empty_text[] = ""; /* inline 0x50c7a4 */
static const int32_t preload_positions[3] = {NEWS_POS_CUR, NEWS_POS_NEXT, NEWS_POS_NEXT2}; /* ROM 0x78c89c */

static const char content_ready_fn[] = "onboarding_news_scroll_content_anim_ready_cb"; /* ROM 0x73a964 */
static const char content_invalid[] = "Invalid content_scroll object"; /* ROM 0x767870 */
static const char content_invalid_short[] = "[onboarding.news]Invalid content_scroll object"; /* ROM 0x73a994 */
static const char widget_closed[] = "Widget already closed, skipping state update"; /* ROM 0x73a9c4 */
static const char widget_closed_short[] =
    "[onboarding.news]Widget already closed, skipping state update"; /* ROM 0x7111a4 */
static const char switch_ready_fn[] = "onboarding_news_container_switch_anim_ready_cb"; /* ROM 0x73a9f4 */
static const char exec_fn[] = "onboarding_news_scroll_anim_exec_cb"; /* ROM 0x75c78c */
static const char exec_invalid[] = "Invalid object, animation stopped"; /* ROM 0x75c7b0 */
static const char exec_invalid_short[] = "[onboarding.news]Invalid object, animation stopped"; /* ROM 0x730098 */
static const char with_anim_fn[] = "onboarding_news_scroll_content_with_anim"; /* ROM 0x746118 */
static const char with_anim_invalid[] = "obj is invalid, skipping animation"; /* ROM 0x75c7d4 */
static const char with_anim_invalid_short[] = "[onboarding.news]obj is invalid, skipping animation"; /* ROM 0x7300cc */
static const char discard_fn[] = "onboarding_news_scroll_discard_read_news_from_fifo"; /* ROM 0x730100 */
static const char discard_failed[] = "Failed to discard news from FIFO (FIFO may be empty)"; /* ROM 0x7256f0 */
static const char discard_failed_short[] =
    "[onboarding.news]Failed to discard news from FIFO (FIFO may be empty)"; /* ROM 0x6fec54 */
static const char load_next_fn[] = "onboarding_news_scroll_load_next_available_news"; /* ROM 0x73aa24 */
static const char load_next_failed[] = "Failed to load news at base_index %d"; /* ROM 0x750a54 */
static const char load_next_failed_short[] = "[onboarding.news]Failed to load news at base_index %d"; /* ROM 0x725728 */
static const char clamp_fn[] = "onboarding_news_scroll_clamp_target_y"; /* ROM 0x750a7c */
static const char clamp_invalid[] = "scroll_obj is invalid, returning target_y as-is"; /* ROM 0x73aa54 */
static const char clamp_invalid_short[] =
    "[onboarding.news]scroll_obj is invalid, returning target_y as-is"; /* ROM 0x707d78 */
static const char down_fn[] = "onboarding_news_scroll_can_scroll_down"; /* ROM 0x750aa4 */
static const char down_none[] = "No container found at position 288"; /* ROM 0x75c7f8 */
static const char down_none_short[] = "[onboarding.news]No container found at position 288"; /* ROM 0x730134 */
static const char down_loaded[] = "Successfully loaded news from FIFO index %d to 288 position"; /* ROM 0x71abd8 */
static const char down_loaded_short[] =
    "[onboarding.news]Successfully loaded news from FIFO index %d to 288 position"; /* ROM 0x6f0b78 */
static const char down_failed[] = "Failed to load news from FIFO index %d to 288 position"; /* ROM 0x725760 */
static const char down_failed_short[] =
    "[onboarding.news]Failed to load news from FIFO index %d to 288 position"; /* ROM 0x6fec9c */
static const char up_fn[] = "onboarding_news_scroll_can_scroll_up"; /* ROM 0x750acc */
static const char up_none[] = "No container found at position -288"; /* ROM 0x75c81c */
static const char up_none_short[] = "[onboarding.news]No container found at position -288"; /* ROM 0x725798 */
static const char reset_fn[] = "onboarding_news_scroll_reset_content_position"; /* ROM 0x73aa84 */
static const char reset_invalid[] = "content_scroll is invalid, skipping reset"; /* ROM 0x746144 */
static const char reset_invalid_short[] = "[onboarding.news]content_scroll is invalid, skipping reset"; /* ROM 0x71ac14 */

#define LOG_FLAGS(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))

static void log0(uint8_t level, const char *fn, uint32_t line, const char *msg, const char *msg_short)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(LOG_FLAGS(level, 0), msg_short, msg_short);
}

static void log1(uint8_t level, const char *fn, uint32_t line, const char *msg, const char *msg_short,
                 uint32_t a)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, msg, a);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(LOG_FLAGS(level, 1), msg_short, msg_short, a);
}

void onboarding_news_scroll_switch_to_prev_news_50bd1c(void);
void onboarding_news_scroll_content_anim_ready_cb_50be4c(void *anim);
void onboarding_news_container_switch_anim_ready_cb_50bfb0(void *a);
void onboarding_news_scroll_anim_exec_cb_50c150(void *obj, int32_t y);
void onboarding_news_scroll_content_with_anim_50c1c0(void *obj, int32_t target_y, int32_t time_ms);
void onboarding_news_scroll_discard_read_news_from_fifo_50c288(void);
uint32_t onboarding_news_scroll_load_next_available_news_50c314(g2_onboarding_news_container_t *c,
                                                                 int32_t base_index);
void onboarding_news_scroll_sync_count_50c3c0(void);
int32_t onboarding_news_scroll_clamp_target_y_50c3f4(void *scroll_obj, int32_t target_y);
g2_onboarding_news_container_t *onboarding_news_find_container_at_50c476(int32_t position_y);
void onboarding_news_container_reset_50c4ac(g2_onboarding_news_container_t *c);
uint32_t onboarding_news_scroll_can_scroll_down_50c528(void);
uint32_t onboarding_news_scroll_can_scroll_up_50c654(void);
void onboarding_news_container_mark_read_50c6cc(g2_onboarding_news_container_t *c);
void onboarding_news_scroll_reset_content_position_50c6e2(g2_onboarding_news_container_t *c);
void onboarding_news_container_anim_exec_cb_50c768(void *var, int32_t delta_y);
void onboarding_news_container_move_with_anim_50c7a8(int32_t direction, int32_t time_ms);
void onboarding_news_scroll_preload_containers_50c868(void);
int32_t onboarding_news_scroll_find_next_unloaded_50c8cc(void);

/* Pops one queued key record from the ext fifo and replays it (inlined in
 * the stock at each completion callback). */
static void replay_queued_input(void)
{
    uint8_t raw[10];
    g2_onboarding_key_msg_t msg;

    if (g2_onboarding_stock_flag_20074db8 != 1 || g2_onboarding_news_ext_fifo_20074db0 == NULL ||
        ui_common_api_fn_00509dfa(g2_onboarding_news_ext_fifo_20074db0) != 0)
        return;
    (void)aeabi_memset_43c0e4(raw, sizeof(raw), 0);
    (void)aeabi_memset_43c0e4(raw, sizeof(raw), 0);
    (void)ui_common_api_fn_00509e14(g2_onboarding_news_ext_fifo_20074db0, raw, 7u);
    if (ui_onboarding_main_sub_004A979C(raw, 0, &msg) == 0)
        onboarding_news_ext_input_event_warpper_50a670(msg.key, msg.value);
}

/* Moves the carousel one slot down (previous news, containers +288) with a
 * 400 ms animation. With no previous news only a queued input is replayed. */
void onboarding_news_scroll_switch_to_prev_news_50bd1c(void)
{
    g2_onboarding_news_scroll_t *m = &g2_onboarding_stock_page_20071048;
    g2_onboarding_news_pending_t *p = &g2_onboarding_news_pending_20073c80;
    g2_onboarding_news_container_t *cur;
    int32_t i;

    onboarding_news_scroll_sync_count_50c3c0();
    if (onboarding_news_scroll_can_scroll_up_50c654() == 0u) {
        replay_queued_input();
        return;
    }
    cur = onboarding_news_find_container_at_50c476(NEWS_POS_CUR);
    if (cur != NULL && cur->data_loaded != 0u)
        onboarding_news_container_mark_read_50c6cc(cur);
    m->is_switching = 1u;
    p->direction = -1;
    p->pending = 1u;
    for (i = 0; i < NEWS_CONTAINERS; i++) {
        g2_onboarding_news_container_t *c = &m->container[i];

        switch (c->position_y) {
        case NEWS_POS_CUR:
            onboarding_news_scroll_reset_content_position_50c6e2(c);
            p->target_y[i] = NEWS_POS_NEXT;
            break;
        case NEWS_POS_NEXT:
            p->target_y[i] = NEWS_POS_NEXT2;
            break;
        case NEWS_POS_NEXT2:
            onboarding_news_container_reset_50c4ac(c);
            p->target_y[i] = NEWS_POS_PREV;
            break;
        case NEWS_POS_PREV:
            onboarding_news_scroll_reset_content_position_50c6e2(c);
            p->target_y[i] = NEWS_POS_CUR;
            break;
        default:
            break;
        }
    }
    onboarding_news_container_move_with_anim_50c7a8(-1, NEWS_SWITCH_ANIM_MS);
}

/* completed_cb of onboarding_news_scroll_content_with_anim. */
void onboarding_news_scroll_content_anim_ready_cb_50be4c(void *anim)
{
    const g2_lv_anim_t *a = anim;
    void *obj;
    int32_t i;

    g2_onboarding_news_anim_kind_2007503e = 0u;
    g2_onboarding_news_anim_obj_20074d8c = NULL;
    obj = a->var;
    if (obj == NULL || audio_terminal_ui_object_valid_43e2ea(obj) == 0u) {
        log0(2u, content_ready_fn, 0x7a2u, content_invalid, content_invalid_short);
        g2_onboarding_news_animating_20074d94 = 0;
        return;
    }
    if (g2_onboarding_stock_flag_20074db8 == 0) {
        log0(2u, content_ready_fn, 0x7a9u, widget_closed, widget_closed_short);
        g2_onboarding_news_animating_20074d94 = 0;
        return;
    }
    for (i = 0; i < NEWS_CONTAINERS; i++) {
        if (g2_onboarding_stock_page_20071048.container[i].content_scroll == obj) {
            onboarding_news_scroll_update_content_state_50b5f4(&g2_onboarding_stock_page_20071048.container[i]);
            break;
        }
    }
    g2_onboarding_news_animating_20074d94 = 0;
    replay_queued_input();
}

/* completed_cb of onboarding_news_container_move_with_anim: commits the
 * pending slot positions, refreshes every container's scroll state and
 * replays one queued input. */
void onboarding_news_container_switch_anim_ready_cb_50bfb0(void *a)
{
    g2_onboarding_news_scroll_t *m = &g2_onboarding_stock_page_20071048;
    g2_onboarding_news_pending_t *p = &g2_onboarding_news_pending_20073c80;
    g2_onboarding_news_container_t *cur;
    int32_t i;

    (void)a;
    g2_onboarding_news_anim_kind_2007503e = 0u;
    g2_onboarding_news_anim_obj_20074d8c = NULL;
    if (p->pending != 0u) {
        for (i = 0; i < NEWS_CONTAINERS; i++) {
            m->container[i].position_y = p->target_y[i];
            if (m->container[i].root != NULL)
                audio_uart_page_43f142(m->container[i].root, p->target_y[i]);
        }
        p->pending = 0u;
        g2_onboarding_news_animating_20074d94 = 0;
    }
    m->is_switching = 0u;
    g2_onboarding_news_animating_20074d94 = 0;
    if (g2_onboarding_stock_flag_20074db8 == 0) {
        log0(2u, switch_ready_fn, 0x7f3u, widget_closed, widget_closed_short);
        return;
    }
    for (i = 0; i < NEWS_CONTAINERS; i++) {
        if (m->container[i].content_scroll != NULL)
            audio_uart_page_43f66c(m->container[i].content_scroll);
    }
    for (i = 0; i < NEWS_CONTAINERS; i++)
        onboarding_news_scroll_update_content_state_50b5f4(&m->container[i]);
    cur = onboarding_news_find_container_at_50c476(NEWS_POS_CUR);
    if (cur != NULL && cur->content_scroll != NULL) {
        audio_uart_page_43f66c(cur->content_scroll);
        onboarding_news_scroll_update_content_state_50b5f4(cur);
        if (cur->scrollable != 0u)
            audio_uart_page_44e368(cur->content_scroll, LV_SCROLLBAR_MODE_AUTO);
        else
            audio_uart_page_44e368(cur->content_scroll, LV_SCROLLBAR_MODE_OFF);
    }
    replay_queued_input();
}

/* exec_cb of the content scroll animation. */
void onboarding_news_scroll_anim_exec_cb_50c150(void *obj, int32_t y)
{
    if (obj != NULL && audio_terminal_ui_object_valid_43e2ea(obj) != 0u) {
        audio_uart_lv_scroll_to_y_44ea04(obj, y, 0u);
        return;
    }
    log0(2u, exec_fn, 0x82cu, exec_invalid, exec_invalid_short);
    g2_onboarding_news_anim_obj_20074d8c = NULL;
}

/* Animates the scroll position of a content object (ease out). */
void onboarding_news_scroll_content_with_anim_50c1c0(void *obj, int32_t target_y, int32_t time_ms)
{
    g2_lv_anim_t a;

    if (obj == NULL)
        return;
    if (audio_terminal_ui_object_valid_43e2ea(obj) == 0u) {
        log0(2u, with_anim_fn, 0x83du, with_anim_invalid, with_anim_invalid_short);
        return;
    }
    g2_onboarding_news_anim_kind_2007503e = 1u;
    g2_onboarding_news_anim_obj_20074d8c = obj;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = obj;
    audio_uart_lv_anim_values_4506ce(&a, audio_uart_lv_obj_y_44e498(obj), target_y);
    a.duration = time_ms;
    a.exec_cb = onboarding_news_scroll_anim_exec_cb_50c150;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.completed_cb = onboarding_news_scroll_content_anim_ready_cb_50be4c;
    g2_onboarding_news_animating_20074d94 = 1;
    (void)audio_uart_lv_anim_start_450408(&a);
}

void onboarding_news_scroll_discard_read_news_from_fifo_50c288(void)
{
    uint8_t ok;

    (void)osMutexAcquire(g2_onboarding_mutex, WAIT_FOREVER);
    ok = onboarding_news_fifo_pop_50b18c(&g2_onboarding_news_record_20061110);
    (void)osMutexRelease(g2_onboarding_mutex);
    if (ok == 0u)
        log0(2u, discard_fn, 0x88du, discard_failed, discard_failed_short);
}

/* Loads FIFO entry base_index into container c. Returns 1 on success. */
uint32_t onboarding_news_scroll_load_next_available_news_50c314(g2_onboarding_news_container_t *c,
                                                                 int32_t base_index)
{
    uint8_t ok;

    if (c == NULL)
        return 0u;
    onboarding_news_scroll_sync_count_50c3c0();
    if (base_index < 0 || base_index >= g2_onboarding_stock_page_20071048.news_count)
        return 0u;
    (void)osMutexAcquire(g2_onboarding_mutex, WAIT_FOREVER);
    ok = onboarding_news_fifo_peek_50b19a(&g2_onboarding_news_record_20061110, (uint16_t)base_index);
    (void)osMutexRelease(g2_onboarding_mutex);
    if (ok == 0u) {
        log1(2u, load_next_fn, 0x8b0u, load_next_failed, load_next_failed_short, (uint32_t)base_index);
        return 0u;
    }
    onboarding_news_scroll_load_news_data_50b438(c, base_index);
    return 1u;
}

void onboarding_news_scroll_sync_count_50c3c0(void)
{
    uint16_t count;

    (void)osMutexAcquire(g2_onboarding_mutex, WAIT_FOREVER);
    count = onboarding_news_fifo_count_50b1ac();
    (void)osMutexRelease(g2_onboarding_mutex);
    g2_onboarding_stock_page_20071048.news_count = count;
}

/* Clamps a scroll target to 0 .. scroll_y + scroll_bottom. */
int32_t onboarding_news_scroll_clamp_target_y_50c3f4(void *scroll_obj, int32_t target_y)
{
    int32_t y;
    int32_t bottom;

    if (scroll_obj == NULL)
        return target_y;
    if (audio_terminal_ui_object_valid_43e2ea(scroll_obj) == 0u) {
        log0(2u, clamp_fn, 0x8c9u, clamp_invalid, clamp_invalid_short);
        return target_y;
    }
    y = audio_uart_lv_obj_y_44e498(scroll_obj);
    bottom = audio_uart_lv_scroll_bottom_44e4bc(scroll_obj);
    if (target_y < 0)
        return 0;
    return target_y <= bottom + y ? target_y : bottom + y;
}

g2_onboarding_news_container_t *onboarding_news_find_container_at_50c476(int32_t position_y)
{
    int32_t i;

    for (i = 0; i < NEWS_CONTAINERS; i++) {
        if (g2_onboarding_stock_page_20071048.container[i].position_y == position_y)
            return &g2_onboarding_stock_page_20071048.container[i];
    }
    return NULL;
}

/* Empties a container that leaves the window. */
void onboarding_news_container_reset_50c4ac(g2_onboarding_news_container_t *c)
{
    if (c == NULL)
        return;
    c->news_id = 0u;
    c->data_loaded = 0u;
    c->flag_27 = 0u;
    c->flag_28 = 0u;
    c->read_count = 0;
    c->scrollable = 0u;
    c->at_top = 1u;
    c->at_bottom = 1u;
    if (c->source_label != NULL)
        audio_uart_page_49942e(c->source_label, empty_text);
    if (c->time_label != NULL)
        audio_uart_page_49942e(c->time_label, empty_text);
    if (c->title_label != NULL)
        audio_uart_page_49942e(c->title_label, empty_text);
    if (c->content_label != NULL)
        audio_uart_page_49942e(c->content_label, empty_text);
}

/* The container below the current one must hold news; it is loaded from
 * the FIFO on demand. Returns 1 when it does. */
uint32_t onboarding_news_scroll_can_scroll_down_50c528(void)
{
    g2_onboarding_news_container_t *c = onboarding_news_find_container_at_50c476(NEWS_POS_NEXT);
    int32_t index;

    if (c == NULL) {
        log0(2u, down_fn, 0x91bu, down_none, down_none_short);
        return 0u;
    }
    if (c->data_loaded == 0u) {
        index = onboarding_news_scroll_find_next_unloaded_50c8cc();
        if (index < 0)
            return 0u;
        if (onboarding_news_scroll_load_next_available_news_50c314(c, index) == 0u) {
            log1(2u, down_fn, 0x92cu, down_failed, down_failed_short, (uint32_t)index);
            return 0u;
        }
        log1(3u, down_fn, 0x929u, down_loaded, down_loaded_short, (uint32_t)index);
    }
    return c->data_loaded != 0u ? 1u : 0u;
}

uint32_t onboarding_news_scroll_can_scroll_up_50c654(void)
{
    g2_onboarding_news_container_t *c = onboarding_news_find_container_at_50c476(NEWS_POS_PREV);

    if (c == NULL) {
        log0(2u, up_fn, 0x948u, up_none, up_none_short);
        return 0u;
    }
    return c->data_loaded;
}

void onboarding_news_container_mark_read_50c6cc(g2_onboarding_news_container_t *c)
{
    if (c != NULL && c->data_loaded != 0u)
        c->read_count++;
}

void onboarding_news_scroll_reset_content_position_50c6e2(g2_onboarding_news_container_t *c)
{
    if (c == NULL || c->data_loaded == 0u || c->content_scroll == NULL)
        return;
    if (audio_terminal_ui_object_valid_43e2ea(c->content_scroll) == 0u) {
        log0(2u, reset_fn, 0x96eu, reset_invalid, reset_invalid_short);
        c->content_scroll = NULL;
        return;
    }
    audio_uart_lv_scroll_to_y_44ea04(c->content_scroll, 0, 0u);
    c->at_top = 1u;
    c->at_bottom = 0u;
    onboarding_news_scroll_update_content_state_50b5f4(c);
}

/* exec_cb of the container switch: every root follows its start y + delta. */
void onboarding_news_container_anim_exec_cb_50c768(void *var, int32_t delta_y)
{
    int32_t i;

    (void)var;
    for (i = 0; i < NEWS_CONTAINERS; i++) {
        void *root = g2_onboarding_stock_page_20071048.container[i].root;

        if (root != NULL && audio_terminal_ui_object_valid_43e2ea(root) != 0u)
            audio_uart_page_43f142(root, g2_onboarding_news_start_y_20073f14[i] + delta_y);
    }
}

/* Moves all containers by one slot: direction >= 1 up (-288), else down
 * (+288). The current content's scrollbar is hidden during the move. */
void onboarding_news_container_move_with_anim_50c7a8(int32_t direction, int32_t time_ms)
{
    g2_onboarding_news_scroll_t *m = &g2_onboarding_stock_page_20071048;
    g2_onboarding_news_container_t *cur;
    g2_lv_anim_t a;
    int32_t delta;
    int32_t i;

    if (m->page_obj == NULL)
        return;
    g2_onboarding_news_anim_kind_2007503e = 2u;
    g2_onboarding_news_anim_obj_20074d8c = NULL;
    for (i = 0; i < NEWS_CONTAINERS; i++) {
        if (m->container[i].root == NULL)
            g2_onboarding_news_start_y_20073f14[i] = 0;
        else
            g2_onboarding_news_start_y_20073f14[i] = audio_uart_lv_obj_y_43fce0(m->container[i].root);
    }
    delta = direction >= 1 ? NEWS_POS_PREV : NEWS_SLOT_H;
    cur = onboarding_news_find_container_at_50c476(NEWS_POS_CUR);
    if (cur != NULL && cur->content_scroll != NULL)
        audio_uart_page_44e368(cur->content_scroll, LV_SCROLLBAR_MODE_OFF);
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = m;
    audio_uart_lv_anim_values_4506ce(&a, 0, delta);
    a.duration = time_ms;
    a.exec_cb = onboarding_news_container_anim_exec_cb_50c768;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.completed_cb = onboarding_news_container_switch_anim_ready_cb_50bfb0;
    g2_onboarding_news_animating_20074d94 = 1;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Fills the empty containers at 0 / 288 / 576 with the next unread news. */
void onboarding_news_scroll_preload_containers_50c868(void)
{
    int32_t positions[3];
    int32_t i;

    onboarding_news_scroll_sync_count_50c3c0();
    if (g2_onboarding_stock_page_20071048.news_count == 0)
        return;
    positions[0] = preload_positions[0];
    positions[1] = preload_positions[1];
    positions[2] = preload_positions[2];
    for (i = 0; i < 3; i++) {
        g2_onboarding_news_container_t *c = onboarding_news_find_container_at_50c476(positions[i]);
        int32_t index;

        if (c == NULL || c->data_loaded != 0u)
            continue;
        index = onboarding_news_scroll_find_next_unloaded_50c8cc();
        if (index >= 0)
            (void)onboarding_news_scroll_load_next_available_news_50c314(c, index);
    }
}

/* First FIFO index whose news id is not shown by a loaded container, or -1. */
int32_t onboarding_news_scroll_find_next_unloaded_50c8cc(void)
{
    g2_onboarding_news_scroll_t *m = &g2_onboarding_stock_page_20071048;
    int32_t i;

    onboarding_news_scroll_sync_count_50c3c0();
    if (m->news_count == 0)
        return -1;
    for (i = 0; i < m->news_count; i++) {
        uint8_t ok;
        uint8_t shown = 0u;
        int32_t j;

        (void)osMutexAcquire(g2_onboarding_mutex, WAIT_FOREVER);
        ok = onboarding_news_fifo_peek_50b19a(&g2_onboarding_news_record_20061110, (uint16_t)i);
        (void)osMutexRelease(g2_onboarding_mutex);
        if (ok == 0u)
            continue;
        for (j = 0; j < NEWS_CONTAINERS; j++) {
            if (m->container[j].data_loaded != 0u &&
                m->container[j].news_id == g2_onboarding_news_record_20061110.id) {
                shown = 1u;
                break;
            }
        }
        if (shown == 0u)
            return i;
    }
    return -1;
}
