/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\common\generic_animation.c
 * Native 0x463c68..0x4642bd; literal pool 0x4642c0..0x46432f.
 *
 * Frame-sequence image animation built on an LVGL image object plus the
 * page fade-in/fade-out opacity animations used by the display thread.
 * The stock style setters used here are LVGL lv_obj_set_style_* wrappers:
 * 0x44127e LV_STYLE_BG_COLOR (28), 0x44129e LV_STYLE_BG_OPA (29),
 * 0x441488 LV_STYLE_OPA (98). */
#include <stdint.h>
#include <stddef.h>

/* User configuration passed to generic_animation_create (caller-owned). */
typedef struct {
    const void *const *frames; /* +0x00 image sources, every entry non-NULL */
    uint32_t frame_count;      /* +0x04 */
    uint32_t period_ms;        /* +0x08 0 selects 50 ms */
    uint8_t mode;              /* +0x0c 0 loop, 1 once, 2 ping-pong */
    uint8_t reserved_0d[3];
    int32_t width;             /* +0x10 applied when > 0 */
    int32_t height;            /* +0x14 applied when > 0 */
    uint8_t color_a[3];        /* +0x18 lv_color_t, stored but not applied */
    uint8_t opa_a;             /* +0x1b */
    uint8_t bg_color[3];       /* +0x1c lv_color_t -> LV_STYLE_BG_COLOR */
    uint8_t bg_opa;            /* +0x1f -> LV_STYLE_BG_OPA */
} g2_generic_animation_config_t;
_Static_assert(sizeof(g2_generic_animation_config_t) == 0x20, "stock config is 32 bytes");

/* Heap instance, 0x2c bytes from file_heap_allocate. */
typedef struct {
    void *image;               /* +0x00 lv_image object */
    const void *const *frames; /* +0x04 */
    uint32_t frame_count;      /* +0x08 */
    uint32_t frame;            /* +0x0c current index */
    uint32_t period_ms;        /* +0x10 */
    uint32_t last_tick;        /* +0x14 osKernelGetTickCount of last step */
    uint8_t running;           /* +0x18 */
    uint8_t mode;              /* +0x19 */
    uint8_t forward;           /* +0x1a ping-pong direction */
    uint8_t finished;          /* +0x1b */
    int32_t width;             /* +0x1c */
    int32_t height;            /* +0x20 */
    uint8_t color_a[3];        /* +0x24 */
    uint8_t opa_a;             /* +0x27 */
    uint8_t bg_color[3];       /* +0x28 */
    uint8_t bg_opa;            /* +0x2b */
} g2_generic_animation_t;
_Static_assert(sizeof(g2_generic_animation_t) == 0x2c, "stock instance is 44 bytes");

enum { ANIM_MODE_LOOP = 0u, ANIM_MODE_ONCE = 1u, ANIM_MODE_PINGPONG = 2u };

/* lv_anim_t (LVGL 9.3 fork) as laid out on the 0x60-byte stack frame. */
typedef struct {
    void *var;                       /* +0x00 */
    void (*exec_cb)(void *, int32_t); /* +0x04 */
    void *custom_exec_cb;            /* +0x08 */
    void *start_cb;                  /* +0x0c */
    void (*completed_cb)(void *);    /* +0x10 */
    void *deleted_cb;                /* +0x14 */
    void *get_value_cb;              /* +0x18 */
    void *user_data;                 /* +0x1c */
    int32_t (*path_cb)(void *);      /* +0x20 */
    int32_t start_value;             /* +0x24 */
    int32_t current_value;           /* +0x28 */
    int32_t end_value;               /* +0x2c */
    int32_t duration;                /* +0x30 */
    uint8_t rest[0x2c];              /* +0x34 */
} g2_lv_anim_t;
_Static_assert(sizeof(g2_lv_anim_t) == 0x60, "stock anim frame is 96 bytes");

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *codec_allocate(uint32_t bytes);                             /* file_heap_allocate 0x474cd2 */
extern void audio_file_heap_free(void *buffer);                          /* file_heap_free 0x474d16 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint32_t osKernelGetTickCount(void);                              /* 0x4490cc */
extern uint8_t audio_uart_device_role_get(void);                         /* 0x45a568 */
extern void *audio_uart_page_498668(void *parent);                       /* lv_image_create */
extern void audio_uart_page_498680(void *image, const void *src);        /* lv_image_set_src */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *object);     /* lv_obj_is_valid */
extern void audio_uart_page_delete_event_filter_44d7b8(void *object);    /* lv_obj_delete */
extern void audio_uart_page_43f506(void *object, int32_t width);         /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *object, int32_t height);        /* lv_obj_set_height */
extern void audio_uart_page_44127e(void *object, uint32_t color, uint32_t selector); /* bg_color */
extern void audio_uart_page_44129e(void *object, uint32_t opa, uint32_t selector);   /* bg_opa */
extern void audio_uart_page_43dfa4(void *object, uint32_t flags);        /* lv_obj_remove_flag */
extern void audio_uart_display_audio_reset_441488(void *object, uint32_t opa, uint32_t selector); /* opa */
extern void audio_uart_lv_anim_init_4503d6(void *anim);
extern void audio_uart_lv_anim_values_4506ce(void *anim, int32_t start, int32_t end);
extern void *audio_uart_lv_anim_start_450408(void *anim);
extern int32_t audio_uart_lv_anim_path_45065a(void *anim);               /* fade-in path */
extern int32_t audio_uart_lv_anim_path_450672(void *anim);               /* fade-out path */
extern void audio_uart_master_display_stop(uint32_t app, const void *payload,
                                           uint16_t length, uint32_t extra); /* 0x464c36 */

void generic_animation_apply_style_463fb0(g2_generic_animation_t *anim);
void generic_animation_next_frame_464008(g2_generic_animation_t *anim);

static const char module_tag[] = "generic.animation"; /* ROM 0x77f6d0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\common\\generic_animation.c"; /* ROM 0x6fad0c */
static const char create_fn[] = "generic_animation_create";   /* ROM 0x76bbac */
static const char destroy_fn[] = "generic_animation_destroy"; /* ROM 0x76bbc8 */
static const char fade_in_fn[] = "fade_in_anim_ready_cb";     /* ROM 0x77790c */
static const char fade_out_fn[] = "_fade_out_anim_ready_cb";  /* ROM 0x777924 */
static const char common_fade_fn[] = "Common_Fadeout_Anim_Start";   /* ROM 0x76bbe4 */
static const char disp_fade_fn[] = "dispThread_Fadeout_Anim_Start"; /* ROM 0x7602b0 */
static const char invalid_params[] = "Invalid parameters"; /* ROM 0x77f6e4 */
static const char invalid_params_short[] = "[generic.animation]Invalid parameters"; /* ROM 0x74a3ac */
static const char alloc_failed[] = "Failed to allocate memory for animation instance"; /* ROM 0x729e14 */
static const char alloc_failed_short[] =
    "[generic.animation]Failed to allocate memory for animation instance"; /* ROM 0x703318 */
static const char image_failed[] = "Failed to create image object"; /* ROM 0x760290 */
static const char image_failed_short[] = "[generic.animation]Failed to create image object"; /* ROM 0x729e48 */
static const char fade_in_done[] =
    "page_fade_in_anim_ready_cb: page fade-in animation completed"; /* ROM 0x70c0e4 */
static const char fade_in_done_short[] =
    "[generic.animation]page_fade_in_anim_ready_cb: page fade-in animation completed"; /* ROM 0x6ed6a8 */
static const char fade_out_done[] =
    "page_fade_out_anim_ready_cb: page fade-out animation completed - screen is now dark"; /* ROM 0x6e8254 */
static const char fade_out_done_short[] =
    "[generic.animation]page_fade_out_anim_ready_cb: page fade-out animation completed - screen is now dark"; /* ROM 0x6d8ba4 */
static const char fade_out_double[] =
    "Starting page fade-out animation (double click detected)"; /* ROM 0x7158a4 */
static const char fade_out_double_short[] =
    "[generic.animation]Starting page fade-out animation (double click detected)"; /* ROM 0x6f3db4 */
static const char fade_out_start[] = "Starting page fade-out animation"; /* ROM 0x754aac */
static const char fade_out_start_short[] = "[generic.animation]Starting page fade-out animation"; /* ROM 0x729e7c */

static void log_error(const char *function, uint32_t line, const char *message, const char *short_message)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module_tag, source_file, function, line, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x04000000u, short_message, short_message);
}

static void log_info(const char *function, uint32_t line, const char *message, const char *short_message)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, function, line, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, short_message, short_message);
}

/* Show frames[index] when the image object is still alive. */
static void show_frame(g2_generic_animation_t *anim, const void *src)
{
    if (anim->image != NULL && audio_terminal_ui_object_valid_43e2ea(anim->image) != 0u)
        audio_uart_page_498680(anim->image, src);
}

/* generic_animation_create: NULL for a bad config, a NULL frame entry, or an
 * allocation/image failure (the frame scan fails silently). */
g2_generic_animation_t *generic_animation_create_463c68(void *parent, const g2_generic_animation_config_t *config)
{
    if (parent == NULL || config == NULL || config->frames == NULL || config->frame_count == 0u) {
        log_error(create_fn, 0x13u, invalid_params, invalid_params_short);
        return NULL;
    }
    for (uint32_t i = 0u; i < config->frame_count; i++) {
        if (config->frames[i] == NULL)
            return NULL;
    }
    g2_generic_animation_t *anim = codec_allocate(sizeof(*anim));
    if (anim == NULL) {
        log_error(create_fn, 0x21u, alloc_failed, alloc_failed_short);
        return NULL;
    }
    audio_uart_buffer_zero(anim, sizeof(*anim), 0u);
    anim->image = audio_uart_page_498668(parent);
    if (anim->image == NULL) {
        audio_file_heap_free(anim);
        log_error(create_fn, 0x2du, image_failed, image_failed_short);
        return NULL;
    }
    anim->frames = config->frames;
    anim->frame_count = config->frame_count;
    anim->period_ms = config->period_ms != 0u ? config->period_ms : 50u;
    anim->mode = config->mode;
    anim->width = config->width;
    anim->height = config->height;
    (void)audio_queue_copy_bytes(anim->color_a, config->color_a, 3u);
    anim->opa_a = config->opa_a;
    (void)audio_queue_copy_bytes(anim->bg_color, config->bg_color, 3u);
    anim->bg_opa = config->bg_opa;
    anim->frame = 0u;
    anim->last_tick = 0u;
    anim->running = 0u;
    anim->forward = 1u;
    anim->finished = 0u;
    generic_animation_apply_style_463fb0(anim);
    if (anim->frames != NULL && anim->frames[0] != NULL)
        audio_uart_page_498680(anim->image, anim->frames[0]);
    return anim;
}

/* generic_animation_destroy: delete_image == 1 also deletes the LVGL image. */
void generic_animation_destroy_463e1c(g2_generic_animation_t *anim, uint8_t delete_image)
{
    if (anim == NULL) {
        log_error(destroy_fn, 0x51u, invalid_params, invalid_params_short);
        return;
    }
    if (delete_image == 1u) {
        if (anim->image != NULL && audio_terminal_ui_object_valid_43e2ea(anim->image) != 0u)
            audio_uart_page_delete_event_filter_44d7b8(anim->image);
        anim->image = NULL;
    }
    anim->frames = NULL;
    anim->frame_count = 0u;
    audio_file_heap_free(anim);
}

void *generic_animation_get_image_463e9a(const g2_generic_animation_t *anim)
{
    return anim != NULL ? anim->image : NULL;
}

void generic_animation_start_463ea6(g2_generic_animation_t *anim)
{
    if (anim == NULL)
        return;
    anim->running = 1u;
    anim->finished = 0u;
    anim->frame = 0u;
    anim->last_tick = osKernelGetTickCount();
    anim->forward = 1u;
    if (anim->frames != NULL && anim->frames[0] != NULL)
        show_frame(anim, anim->frames[0]);
}

void generic_animation_stop_463eee(g2_generic_animation_t *anim)
{
    if (anim == NULL)
        return;
    anim->running = 0u;
    anim->finished = 0u;
    anim->frame = 0u;
    anim->last_tick = 0u;
    anim->forward = 1u;
    if (anim->frames != NULL && anim->frames[0] != NULL)
        show_frame(anim, anim->frames[0]);
}

/* Periodic tick: advance one frame once period_ms has elapsed. */
void generic_animation_update_463f34(g2_generic_animation_t *anim)
{
    if (anim == NULL || anim->running != 1u)
        return;
    uint32_t now = osKernelGetTickCount();
    if (now - anim->last_tick >= anim->period_ms) {
        anim->last_tick = now;
        generic_animation_next_frame_464008(anim);
    }
}

void generic_animation_set_frame_463f5c(g2_generic_animation_t *anim, uint32_t frame)
{
    if (anim == NULL || frame >= anim->frame_count)
        return;
    anim->last_tick = osKernelGetTickCount();
    anim->frame = frame;
    if (anim->frames != NULL && anim->frames[frame] != NULL)
        show_frame(anim, anim->frames[frame]);
}

uint32_t generic_animation_get_frame_463fa4(const g2_generic_animation_t *anim)
{
    return anim != NULL ? anim->frame : 0u;
}

/* Size, background color/opacity and flag 2 (LV_OBJ_FLAG_CLICKABLE) removal.
 * The colour is copied into a word and passed by value (lv_color_t). */
void generic_animation_apply_style_463fb0(g2_generic_animation_t *anim)
{
    if (anim == NULL || anim->image == NULL)
        return;
    if (anim->width > 0)
        audio_uart_page_43f506(anim->image, anim->width);
    if (anim->height > 0)
        audio_uart_page_43f568(anim->image, anim->height);
    uint32_t color = 0u;
    (void)audio_queue_copy_bytes(&color, anim->bg_color, 3u);
    audio_uart_page_44127e(anim->image, color, 0u);
    audio_uart_page_44129e(anim->image, anim->bg_opa, 0u);
    audio_uart_page_43dfa4(anim->image, 2u);
}

/* Step rules: loop wraps; once stops on the last frame (finished = 1);
 * ping-pong reverses at either end; any other mode stops immediately. */
void generic_animation_next_frame_464008(g2_generic_animation_t *anim)
{
    if (anim == NULL || anim->frames == NULL)
        return;
    uint32_t next;
    if (anim->mode == ANIM_MODE_LOOP) {
        next = anim->frame + 1u;
        if (next >= anim->frame_count)
            next = 0u;
    } else if (anim->mode == ANIM_MODE_PINGPONG) {
        if (anim->forward == 0u) {
            if (anim->frame == 0u) {
                anim->forward = 1u;
                next = anim->frame + 1u;
            } else {
                next = anim->frame - 1u;
            }
        } else if (anim->frame < anim->frame_count - 1u) {
            next = anim->frame + 1u;
        } else {
            anim->forward = 0u;
            next = anim->frame - 1u;
        }
    } else if (anim->mode < ANIM_MODE_PINGPONG) {
        if (anim->frame >= anim->frame_count - 1u) {
            anim->finished = 1u;
            anim->running = 0u;
            return;
        }
        next = anim->frame + 1u;
    } else {
        anim->finished = 1u;
        anim->running = 0u;
        return;
    }
    if (next >= anim->frame_count)
        next = 0u;
    anim->frame = next;
    if (anim->image != NULL && audio_terminal_ui_object_valid_43e2ea(anim->image) != 0u &&
        anim->frames[next] != NULL)
        audio_uart_page_498680(anim->image, anim->frames[next]);
}

/* lv_anim completed_cb of the page fade-in. */
void fade_in_anim_ready_cb_4640c0(void *a)
{
    (void)a;
    log_info(fade_in_fn, 0x1a7u, fade_in_done, fade_in_done_short);
}

/* lv_anim exec_cb of the page fade-in: LV_STYLE_OPA on the main part. */
void fade_in_anim_set_opa_4640fe(void *object, int32_t value)
{
    audio_uart_display_audio_reset_441488(object, (uint8_t)value, 0u);
}

/* Page fade-in: opacity 0 -> 255 over 250 ms. */
void page_fade_in_anim_start_46410a(void *object)
{
    g2_lv_anim_t a;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = object;
    audio_uart_lv_anim_values_4506ce(&a, 0, 0xff);
    a.duration = 250;
    a.exec_cb = fade_in_anim_set_opa_4640fe;
    a.path_cb = audio_uart_lv_anim_path_45065a;
    a.completed_cb = fade_in_anim_ready_cb_4640c0;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* lv_anim exec_cb of the page fade-out (separate stock copy). */
void fade_out_anim_set_opa_464152(void *object, int32_t value)
{
    audio_uart_display_audio_reset_441488(object, (uint8_t)value, 0u);
}

/* lv_anim completed_cb of Common_Fadeout_Anim_Start: user_data is the
 * application id; the master then asks the schedule manager to stop it. */
void fade_out_anim_ready_cb_46415e(void *a)
{
    uint32_t app = (uint32_t)(uintptr_t)((g2_lv_anim_t *)a)->user_data;
    log_info(fade_out_fn, 0x1d2u, fade_out_done, fade_out_done_short);
    if (audio_uart_device_role_get() == 1u)
        audio_uart_master_display_stop(app, NULL, 0u, 0u);
}

/* Double-click exit: opacity 255 -> 0 over 250 ms, then stop the app. */
void Common_Fadeout_Anim_Start_4641b6(void *object, uint32_t app)
{
    log_info(common_fade_fn, 0x1dcu, fade_out_double, fade_out_double_short);
    g2_lv_anim_t a;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = object;
    audio_uart_lv_anim_values_4506ce(&a, 0xff, 0);
    a.duration = 250;
    a.exec_cb = fade_out_anim_set_opa_464152;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.user_data = (void *)(uintptr_t)app;
    a.completed_cb = fade_out_anim_ready_cb_46415e;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Display-thread fade-out with caller duration and no completion callback. */
void dispThread_Fadeout_Anim_Start_464242(void *object, uint32_t duration_ms)
{
    log_info(disp_fade_fn, 0x1efu, fade_out_start, fade_out_start_short);
    g2_lv_anim_t a;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = object;
    audio_uart_lv_anim_values_4506ce(&a, 0xff, 0);
    a.duration = (int32_t)duration_ms;
    a.exec_cb = fade_out_anim_set_opa_464152;
    a.path_cb = audio_uart_lv_anim_path_450672;
    (void)audio_uart_lv_anim_start_450408(&a);
}
