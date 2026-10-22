/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenAI\even_ai_animation.c
 * Native 0x55341c..0x553d3b and 0x553d64..0x553fe7; literal pools
 * 0x553d3c..0x553d63 and 0x553fe8..0x55407f. The first four rows carry
 * inventory names from the neighbouring text_stream_service.c module.
 *
 * Four phase animations (generic_animation frame sequences, 36x20 px, 50 ms
 * per frame) are created once on the Even AI page. The master eye (device role
 * 1) sends a sync record whenever its animation crosses a 6-frame gate, loops,
 * finishes or turns around; the slave eye (role 2) stops at the next gate until
 * apply_sync catches it up. */
#include <stdint.h>
#include <stddef.h>

enum { EVEN_AI_ANIM_PHASES = 4u, EVEN_AI_SYNC_GATE_FRAMES = 6u };
enum { DEVICE_ROLE_MASTER = 1u, DEVICE_ROLE_SLAVE = 2u };
enum { ANIM_MODE_LOOP = 0u, ANIM_MODE_ONCE = 1u, ANIM_MODE_PINGPONG = 2u };
enum { LV_OBJ_FLAG_HIDDEN = 0x1u };

/* generic_animation.c config / instance (see ui/a-10-generic-animation). */
typedef struct {
    const void *const *frames; /* +0x00 */
    uint32_t frame_count;      /* +0x04 */
    uint32_t period_ms;        /* +0x08 */
    uint8_t mode;              /* +0x0c */
    uint8_t reserved_0d[3];
    int32_t width;             /* +0x10 */
    int32_t height;            /* +0x14 */
    uint8_t color_a[3];        /* +0x18 */
    uint8_t opa_a;             /* +0x1b */
    uint8_t bg_color[3];       /* +0x1c */
    uint8_t bg_opa;            /* +0x1f */
} g2_generic_animation_config_t;
_Static_assert(sizeof(g2_generic_animation_config_t) == 0x20, "stock config is 32 bytes");

typedef struct {
    void *image;               /* +0x00 */
    const void *const *frames; /* +0x04 */
    uint32_t frame_count;      /* +0x08 */
    uint32_t frame;            /* +0x0c */
    uint32_t period_ms;        /* +0x10 */
    uint32_t last_tick;        /* +0x14 */
    uint8_t running;           /* +0x18 */
    uint8_t mode;              /* +0x19 */
    uint8_t forward;           /* +0x1a ping-pong direction */
    uint8_t finished;          /* +0x1b */
    uint8_t reserved_1c[0x10];
} g2_generic_animation_t;
_Static_assert(sizeof(g2_generic_animation_t) == 0x2c, "stock instance is 44 bytes");

/* Animation preset table (RAM 0x200733c8, 0x34 bytes). */
typedef struct {
    struct {
        const void *const *frames;
        uint32_t frame_count;
    } phase[EVEN_AI_ANIM_PHASES]; /* +0x00 */
    uint32_t period_ms;           /* +0x20 also the idle hold time */
    int32_t width;                /* +0x24 */
    int32_t height;               /* +0x28 */
    uint32_t reserved_2c;
    uint8_t color[3];             /* +0x30 */
    uint8_t opa;                  /* +0x33 */
} g2_even_ai_anim_presets_t;
_Static_assert(sizeof(g2_even_ai_anim_presets_t) == 0x34, "stock preset table is 52 bytes");

/* Per-phase sync bookkeeping (RAM 0x200730f4, 4 x 0x10 bytes). */
typedef struct {
    uint8_t waiting;       /* +0x00 slave paused at a gate */
    uint8_t reserved_01[3];
    uint32_t master_gate;  /* +0x04 last gate the master sent */
    uint32_t slave_gate;   /* +0x08 last gate received by the slave */
    uint8_t direction;     /* +0x0c master ping-pong direction */
    uint8_t once_finished; /* +0x0d */
    uint8_t reserved_0e[2];
} g2_even_ai_anim_sync_t;
_Static_assert(sizeof(g2_even_ai_anim_sync_t) == 0x10, "stock sync record is 16 bytes");

/* Sync record sent over the inter-eye sync interface (type 7, 8 bytes). */
typedef struct {
    uint8_t cmd;        /* 6 */
    uint8_t phase;
    uint8_t frame[4];   /* little-endian */
    uint8_t forward;
    uint8_t finished;
} g2_even_ai_anim_sync_msg_t;
_Static_assert(sizeof(g2_even_ai_anim_sync_msg_t) == 8, "stock sync message is 8 bytes");

extern uint8_t g2_even_ai_anim_initialized_20074fc2;          /* RAM 0x20074fc2 */
extern void *g2_even_ai_anim_parent_20074584;                 /* RAM 0x20074584 */
extern const void *const g2_even_ai_anim_frames_200009c0[];   /* RAM 0x200009c0, 18 frames */
extern const void *const g2_even_ai_anim_frames_20000a08[];   /* RAM 0x20000a08, 19 frames */
extern const void *const g2_even_ai_anim_frames_20000a54[];   /* RAM 0x20000a54, 25 frames */
extern const void *const g2_even_ai_anim_frames_20000ab8[];   /* RAM 0x20000ab8, 16 frames */
extern g2_even_ai_anim_presets_t g2_even_ai_anim_presets_200733c8; /* RAM 0x200733c8 */
extern g2_generic_animation_t *g2_even_ai_anims_20073e44[EVEN_AI_ANIM_PHASES]; /* RAM 0x20073e44 */
extern uint8_t g2_even_ai_anim_phase_20074fc1;                /* RAM 0x20074fc1 current phase */
extern g2_even_ai_anim_sync_t g2_even_ai_anim_sync_200730f4[EVEN_AI_ANIM_PHASES]; /* RAM 0x200730f4 */
extern uint8_t g2_even_ai_anim_shown_phase_20004547;          /* RAM 0x20004547 */
extern int8_t g2_even_ai_anim_last_phase_20004548;            /* RAM 0x20004548 phase of the previous update */
extern uint32_t g2_even_ai_anim_hold_tick_20074588;           /* RAM 0x20074588 */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void audio_uart_lv_memzero_48949c(void *dst, uint32_t len);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint32_t osKernelGetTickCount(void);                     /* 0x4490cc */
extern uint32_t display_driver_uled_mode_45a568(void);          /* device role */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);           /* lv_color_hex */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);   /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);   /* lv_obj_remove_flag */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel); /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel); /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel); /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel); /* pad_right */
extern g2_generic_animation_t *generic_animation_create_463c68(void *parent, const g2_generic_animation_config_t *config);
extern void generic_animation_destroy_463e1c(g2_generic_animation_t *anim, uint8_t delete_image);
extern void *generic_animation_get_image_463e9a(const g2_generic_animation_t *anim);
extern void generic_animation_start_463ea6(g2_generic_animation_t *anim);
extern void generic_animation_stop_463eee(g2_generic_animation_t *anim);
extern void generic_animation_update_463f34(g2_generic_animation_t *anim);
extern void generic_animation_set_frame_463f5c(g2_generic_animation_t *anim, uint32_t frame);
extern uint32_t generic_animation_get_frame_463fa4(const g2_generic_animation_t *anim);
extern void audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                              uint32_t flags); /* 0x464bb2 inter-eye sync send */

static const char module_tag[] = "even_ai.animation"; /* ROM 0x77f360 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\even_ai_animation.c"; /* ROM 0x6fa25c */
static const char fn_show_phase[] = "even_ai_animation_show_phase"; /* ROM 0x75fdd0 */
static const char fn_update[] = "even_ai_animation_update"; /* ROM 0x76b6c0 */
static const char fn_apply_sync[] = "even_ai_animation_apply_sync"; /* ROM 0x75fdf0 */
static const char no_phase[] = "Animation phase %d does not exist"; /* ROM 0x7543ec */
static const char no_phase_short[] = "[even_ai.animation]Animation phase %d does not exist"; /* ROM 0x71eb18 */
static const char slave_wait[] = "Slave animation waiting for sync at frame %lu, gate %lu"; /* ROM 0x71eb50 */
static const char slave_wait_short[] = "[even_ai.animation]Slave animation waiting for sync at frame %lu, gate %lu"; /* ROM 0x6f326c */
static const char master_loop[] = "Master LOOP: looped from %lu to %lu"; /* ROM 0x754410 */
static const char master_loop_short[] = "[even_ai.animation]Master LOOP: looped from %lu to %lu"; /* ROM 0x71eb88 */
static const char master_once[] = "Master ONCE: finished at frame %lu"; /* ROM 0x754434 */
static const char master_once_short[] = "[even_ai.animation]Master ONCE: finished at frame %lu"; /* ROM 0x71ebc0 */
static const char dir_forward[] = "forward"; /* ROM 0x78d534 */
static const char dir_backward[] = "backward"; /* ROM 0x78a9f4 */
static const char master_pingpong[] = "Master PING_PONG: direction changed to %s at frame %lu"; /* ROM 0x71ebf8 */
static const char master_pingpong_short[] = "[even_ai.animation]Master PING_PONG: direction changed to %s at frame %lu"; /* ROM 0x6f32b8 */
static const char dir_fwd[] = "fwd"; /* ROM 0x553d3c */
static const char dir_bwd[] = "bwd"; /* ROM 0x553d40 */
static const char master_sync[] = "Master sent sync: phase=%d, frame=%lu, gate=%lu, dir=%s"; /* ROM 0x71ec30 */
static const char master_sync_short[] = "[even_ai.animation]Master sent sync: phase=%d, frame=%lu, gate=%lu, dir=%s"; /* ROM 0x6f3304 */
static const char sync_uninit[] = "Animation sync failed: not initialized or invalid phase %d"; /* ROM 0x714b84 */
static const char sync_uninit_short[] = "[even_ai.animation]Animation sync failed: not initialized or invalid phase %d"; /* ROM 0x6eced8 */
static const char sync_missing[] = "Animation sync failed: phase %d animation does not exist"; /* ROM 0x714bc0 */
static const char sync_missing_short[] = "[even_ai.animation]Animation sync failed: phase %d animation does not exist"; /* ROM 0x6f3350 */
static const char slave_loop[] = "Slave LOOP: detected master loop, jumping from %lu to %lu"; /* ROM 0x714bfc */
static const char slave_loop_short[] = "[even_ai.animation]Slave LOOP: detected master loop, jumping from %lu to %lu"; /* ROM 0x6ecf28 */
static const char slave_once[] = "Slave ONCE: catching up from %lu to %lu"; /* ROM 0x749e84 */
static const char slave_once_short[] = "[even_ai.animation]Slave ONCE: catching up from %lu to %lu"; /* ROM 0x714c38 */
static const char slave_pingpong[] = "Slave PING_PONG: syncing from %lu to %lu"; /* ROM 0x73eb30 */
static const char slave_pingpong_short[] = "[even_ai.animation]Slave PING_PONG: syncing from %lu to %lu"; /* ROM 0x714c74 */
static const char slave_resumed[] = "Slave animation resumed from sync wait at frame %lu"; /* ROM 0x72958c */
static const char slave_resumed_short[] = "[even_ai.animation]Slave animation resumed from sync wait at frame %lu"; /* ROM 0x6fa2a4 */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

void text_stream_animation_presets_deinit(void);

/* Non-inlined copy of LVGL lv_obj_set_style_pad_all. */
void text_stream_apply_animation_bounds(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

static void create_phase(void *parent, uint32_t index)
{
    const g2_even_ai_anim_presets_t *p = &g2_even_ai_anim_presets_200733c8;
    g2_generic_animation_config_t cfg;

    if (p->phase[index].frames == NULL || p->phase[index].frame_count == 0u)
        return;
    audio_uart_lv_memzero_48949c(&cfg, sizeof(cfg));
    cfg.frames = p->phase[index].frames;
    cfg.frame_count = p->phase[index].frame_count;
    cfg.period_ms = p->period_ms == 0u ? 50u : p->period_ms;
    cfg.width = p->width;
    cfg.height = p->height;
    (void)audio_queue_copy_bytes(cfg.color_a, p->color, 3u);
    cfg.opa_a = p->opa;
    g2_even_ai_anims_20073e44[index] = generic_animation_create_463c68(parent, &cfg);
    if (g2_even_ai_anims_20073e44[index] == NULL)
        return;
    void *image = generic_animation_get_image_463e9a(g2_even_ai_anims_20073e44[index]);
    if (image == NULL)
        return;
    text_stream_apply_animation_bounds(image, 0, 0u);
    audio_uart_page_44122a(image, 8, 0u);
    audio_uart_page_441238(image, 8, 0u);
    audio_uart_page_43ded4(image, LV_OBJ_FLAG_HIDDEN);
}

/* even_ai_animation_init: returns -1 for a NULL parent, 0 otherwise; an
 * existing set is rebuilt only when force is 1. */
int32_t text_stream_animation_presets_init(void *parent, uint8_t force)
{
    g2_even_ai_anim_presets_t presets;
    uint32_t black;

    if (parent == NULL)
        return -1;
    if (g2_even_ai_anim_initialized_20074fc2 != 0u) {
        if (force != 1u)
            return 0;
        text_stream_animation_presets_deinit();
    }
    g2_even_ai_anim_parent_20074584 = parent;
    audio_uart_lv_memzero_48949c(&presets, sizeof(presets));
    presets.phase[0].frames = g2_even_ai_anim_frames_200009c0;
    presets.phase[0].frame_count = 0x12u;
    presets.phase[1].frames = g2_even_ai_anim_frames_20000a08;
    presets.phase[1].frame_count = 0x13u;
    presets.phase[2].frames = g2_even_ai_anim_frames_20000a54;
    presets.phase[2].frame_count = 0x19u;
    presets.phase[3].frames = g2_even_ai_anim_frames_20000ab8;
    presets.phase[3].frame_count = 0x10u;
    presets.period_ms = 0x32u;
    presets.width = 0x24;
    presets.height = 0x14;
    black = audio_uart_page_44104c(0u);
    (void)audio_queue_copy_bytes(presets.color, &black, 3u);
    presets.opa = 0xffu;
    (void)audio_queue_copy_bytes(&g2_even_ai_anim_presets_200733c8, &presets, sizeof(presets));

    for (uint32_t i = 0u; i < EVEN_AI_ANIM_PHASES; i++)
        create_phase(parent, i);

    g2_even_ai_anim_initialized_20074fc2 = 1u;
    g2_even_ai_anim_phase_20074fc1 = 0u;
    (void)aeabi_memset_43c0e4(g2_even_ai_anim_sync_200730f4, sizeof(g2_even_ai_anim_sync_200730f4), 0);
    return 0;
}

void text_stream_animation_presets_deinit(void)
{
    if (g2_even_ai_anim_initialized_20074fc2 == 0u)
        return;
    for (int32_t i = 0; i < (int32_t)EVEN_AI_ANIM_PHASES; i++) {
        if (g2_even_ai_anims_20073e44[i] != NULL) {
            generic_animation_destroy_463e1c(g2_even_ai_anims_20073e44[i], 0u);
            g2_even_ai_anims_20073e44[i] = NULL;
        }
    }
    (void)aeabi_memset_43c0e4(&g2_even_ai_anim_presets_200733c8, sizeof(g2_even_ai_anim_presets_200733c8), 0);
    (void)aeabi_memset_43c0e4(g2_even_ai_anim_sync_200730f4, sizeof(g2_even_ai_anim_sync_200730f4), 0);
    g2_even_ai_anim_parent_20074584 = NULL;
    g2_even_ai_anim_initialized_20074fc2 = 0u;
    g2_even_ai_anim_phase_20074fc1 = 0u;
}

/* even_ai_animation_get_image */
void *text_stream_animation_preset_get(uint8_t phase)
{
    if (g2_even_ai_anim_initialized_20074fc2 == 0u || phase > 3u)
        return NULL;
    if (g2_even_ai_anims_20073e44[phase] == NULL)
        return NULL;
    return generic_animation_get_image_463e9a(g2_even_ai_anims_20073e44[phase]);
}

void even_ai_animation_hide_all_55389a(void);

int32_t even_ai_animation_show_phase_5537cc(uint8_t phase)
{
    if (g2_even_ai_anim_initialized_20074fc2 == 0u || phase > 3u)
        return -1;
    if (g2_even_ai_anims_20073e44[phase] == NULL) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_show_phase, 0x118u, no_phase, phase);
        if (log_compressed_on())
            (void)compress_log_output(0x04400000u, no_phase_short, no_phase_short, phase);
        return -1;
    }
    even_ai_animation_hide_all_55389a();
    void *image = generic_animation_get_image_463e9a(g2_even_ai_anims_20073e44[phase]);
    if (image != NULL)
        audio_uart_page_43dfa4(image, LV_OBJ_FLAG_HIDDEN);
    generic_animation_start_463ea6(g2_even_ai_anims_20073e44[phase]);
    (void)aeabi_memset_43c0e4(&g2_even_ai_anim_sync_200730f4[phase], sizeof(g2_even_ai_anim_sync_t), 0);
    g2_even_ai_anim_phase_20074fc1 = phase;
    g2_even_ai_anim_shown_phase_20004547 = phase;
    return 0;
}

void even_ai_animation_hide_all_55389a(void)
{
    if (g2_even_ai_anim_initialized_20074fc2 == 0u)
        return;
    for (int32_t i = 0; i < (int32_t)EVEN_AI_ANIM_PHASES; i++) {
        if (g2_even_ai_anims_20073e44[i] != NULL) {
            generic_animation_stop_463eee(g2_even_ai_anims_20073e44[i]);
            void *image = generic_animation_get_image_463e9a(g2_even_ai_anims_20073e44[i]);
            if (image != NULL)
                audio_uart_page_43ded4(image, LV_OBJ_FLAG_HIDDEN);
        }
    }
}

/* even_ai_animation_update: advance the current phase animation one tick. */
void even_ai_animation_process_5538d8(void)
{
    if (g2_even_ai_anim_initialized_20074fc2 == 0u)
        return;

    /* phase 0 held at its last frame for one period, then restarted at frame 2 */
    if (g2_even_ai_anim_phase_20074fc1 == 0u && g2_even_ai_anim_last_phase_20004548 == 0) {
        uint32_t now = osKernelGetTickCount();
        uint32_t frame = generic_animation_get_frame_463fa4(g2_even_ai_anims_20073e44[g2_even_ai_anim_phase_20074fc1]);
        if (frame == g2_even_ai_anim_presets_200733c8.phase[3].frame_count - 1u) {
            if (g2_even_ai_anim_hold_tick_20074588 == 0u) {
                g2_even_ai_anim_hold_tick_20074588 = now;
            } else if (now - g2_even_ai_anim_hold_tick_20074588 >= g2_even_ai_anim_presets_200733c8.period_ms) {
                generic_animation_set_frame_463f5c(g2_even_ai_anims_20073e44[g2_even_ai_anim_phase_20074fc1], 2u);
                g2_even_ai_anim_hold_tick_20074588 = 0u;
                return;
            }
        } else {
            g2_even_ai_anim_hold_tick_20074588 = 0u;
        }
    }

    uint8_t role = (uint8_t)display_driver_uled_mode_45a568();
    if (role == DEVICE_ROLE_SLAVE && g2_even_ai_anims_20073e44[g2_even_ai_anim_phase_20074fc1] != NULL) {
        g2_even_ai_anim_sync_t *sync = &g2_even_ai_anim_sync_200730f4[g2_even_ai_anim_phase_20074fc1];
        uint32_t frame = generic_animation_get_frame_463fa4(g2_even_ai_anims_20073e44[g2_even_ai_anim_phase_20074fc1]);
        uint32_t gate_frame = (sync->slave_gate + 1u) * EVEN_AI_SYNC_GATE_FRAMES;
        if (frame >= gate_frame && sync->waiting == 0u) {
            sync->waiting = 1u;
            if (log_extended_on())
                audio_log_extended(4u, module_tag, source_file, fn_update, 0x174u, slave_wait, frame, gate_frame);
            if (log_compressed_on())
                (void)compress_log_output(0x10800000u, slave_wait_short, slave_wait_short, frame, gate_frame);
        }
        if (sync->waiting != 0u)
            return;
    }

    g2_generic_animation_t *anim = g2_even_ai_anims_20073e44[g2_even_ai_anim_phase_20074fc1];
    if (anim != NULL) {
        uint32_t before = generic_animation_get_frame_463fa4(anim);
        uint8_t forward_before = anim->forward;
        uint8_t finished_before = anim->finished;
        uint8_t mode = anim->mode;
        generic_animation_update_463f34(anim);
        uint32_t frame = generic_animation_get_frame_463fa4(anim);
        uint8_t forward = anim->forward;
        uint8_t finished = anim->finished;

        if (role == DEVICE_ROLE_MASTER) {
            g2_even_ai_anim_sync_t *sync = &g2_even_ai_anim_sync_200730f4[g2_even_ai_anim_phase_20074fc1];
            uint8_t send = 0u;
            uint8_t event = 0u;

            if (mode == ANIM_MODE_LOOP) {
                if (frame < before) {
                    sync->master_gate = 0u;
                    send = 1u;
                    event = 1u;
                    if (log_extended_on())
                        audio_log_extended(4u, module_tag, source_file, fn_update, 0x199u, master_loop, before, frame);
                    if (log_compressed_on())
                        (void)compress_log_output(0x10800000u, master_loop_short, master_loop_short, before, frame);
                }
            } else if (mode == ANIM_MODE_ONCE) {
                if (finished_before == 0u && finished != 0u) {
                    send = 1u;
                    event = 1u;
                    sync->once_finished = 1u;
                    if (log_extended_on())
                        audio_log_extended(4u, module_tag, source_file, fn_update, 0x1a2u, master_once, frame);
                    if (log_compressed_on())
                        (void)compress_log_output(0x10400000u, master_once_short, master_once_short, frame);
                }
            } else if (mode == ANIM_MODE_PINGPONG && forward_before != forward) {
                if (forward == 0u)
                    sync->master_gate = (anim->frame_count - 1u) / EVEN_AI_SYNC_GATE_FRAMES;
                else
                    sync->master_gate = 0u;
                send = 1u;
                event = 1u;
                sync->direction = forward;
                if (log_extended_on())
                    audio_log_extended(4u, module_tag, source_file, fn_update, 0x1b4u, master_pingpong,
                                       forward != 0u ? dir_forward : dir_backward, frame);
                if (log_compressed_on())
                    (void)compress_log_output(0x10800000u, master_pingpong_short, master_pingpong_short,
                                              forward != 0u ? dir_forward : dir_backward, frame);
            }

            if (event == 0u && frame != before) {
                uint32_t gate = frame / EVEN_AI_SYNC_GATE_FRAMES;
                if (frame != 0u && frame % EVEN_AI_SYNC_GATE_FRAMES == 0u &&
                    (sync->master_gate < gate || gate < sync->master_gate)) {
                    send = 1u;
                    sync->master_gate = gate;
                }
            }
            if (send != 0u) {
                g2_even_ai_anim_sync_msg_t msg;
                msg.cmd = 6u;
                msg.phase = g2_even_ai_anim_phase_20074fc1;
                msg.frame[0] = (uint8_t)frame;
                msg.frame[1] = (uint8_t)(frame >> 8);
                msg.frame[2] = (uint8_t)(frame >> 16);
                msg.frame[3] = (uint8_t)(frame >> 24);
                msg.forward = forward != 0u ? 1u : 0u;
                msg.finished = finished != 0u ? 1u : 0u;
                audio_uart_master_display_refresh(7u, &msg, sizeof(msg), 0u);
                if (event == 0u) {
                    if (log_extended_on())
                        audio_log_extended(4u, module_tag, source_file, fn_update, 0x1d7u, master_sync,
                                           g2_even_ai_anim_phase_20074fc1, frame, sync->master_gate,
                                           forward != 0u ? dir_fwd : dir_bwd);
                    if (log_compressed_on())
                        (void)compress_log_output(0x11000000u, master_sync_short, master_sync_short,
                                                  g2_even_ai_anim_phase_20074fc1, frame, sync->master_gate,
                                                  forward != 0u ? dir_fwd : dir_bwd);
                }
            }
        }
    }
    g2_even_ai_anim_last_phase_20004548 = (int8_t)g2_even_ai_anim_phase_20074fc1;
}

uint8_t even_ai_animation_phase_get_553d28(void)
{
    if (g2_even_ai_anim_initialized_20074fc2 == 0u)
        return 0u;
    return g2_even_ai_anim_phase_20074fc1;
}

/* Slave side of the sync record: jump to the master frame where needed and
 * release a gate wait. */
void even_ai_animation_apply_sync_553d64(uint8_t phase, uint32_t frame)
{
    if (g2_even_ai_anim_initialized_20074fc2 == 0u || phase > 3u) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_apply_sync, 0x23cu, sync_uninit, phase);
        if (log_compressed_on())
            (void)compress_log_output(0x08400000u, sync_uninit_short, sync_uninit_short, phase);
        return;
    }
    if (g2_even_ai_anims_20073e44[phase] == NULL) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_apply_sync, 0x241u, sync_missing, phase);
        if (log_compressed_on())
            (void)compress_log_output(0x08400000u, sync_missing_short, sync_missing_short, phase);
        return;
    }
    if ((uint8_t)display_driver_uled_mode_45a568() != DEVICE_ROLE_SLAVE)
        return;

    g2_even_ai_anim_sync_t *sync = &g2_even_ai_anim_sync_200730f4[phase];
    g2_generic_animation_t *anim = g2_even_ai_anims_20073e44[phase];
    uint32_t current = generic_animation_get_frame_463fa4(anim);
    uint8_t mode = anim->mode;
    uint8_t jump = 0u;

    if (mode == ANIM_MODE_LOOP) {
        if (frame < current && (anim->frame_count >> 1) < current - frame) {
            sync->slave_gate = 0u;
            sync->waiting = 0u;
            jump = 1u;
            if (log_extended_on())
                audio_log_extended(4u, module_tag, source_file, fn_apply_sync, 0x25du, slave_loop, current, frame);
            if (log_compressed_on())
                (void)compress_log_output(0x10800000u, slave_loop_short, slave_loop_short, current, frame);
        } else if (current < frame) {
            jump = 1u;
        }
    } else if (mode == ANIM_MODE_ONCE) {
        if (current < frame) {
            jump = 1u;
            if (log_extended_on())
                audio_log_extended(4u, module_tag, source_file, fn_apply_sync, 0x266u, slave_once, current, frame);
            if (log_compressed_on())
                (void)compress_log_output(0x10800000u, slave_once_short, slave_once_short, current, frame);
        }
    } else if (mode == ANIM_MODE_PINGPONG && current != frame) {
        jump = 1u;
        if (log_extended_on())
            audio_log_extended(4u, module_tag, source_file, fn_apply_sync, 0x26eu, slave_pingpong, current, frame);
        if (log_compressed_on())
            (void)compress_log_output(0x10800000u, slave_pingpong_short, slave_pingpong_short, current, frame);
    }
    sync->slave_gate = frame / EVEN_AI_SYNC_GATE_FRAMES;
    if (jump != 0u)
        generic_animation_set_frame_463f5c(anim, frame);
    if (sync->waiting != 0u) {
        sync->waiting = 0u;
        if (log_extended_on())
            audio_log_extended(4u, module_tag, source_file, fn_apply_sync, 0x27eu, slave_resumed, frame);
        if (log_compressed_on())
            (void)compress_log_output(0x10400000u, slave_resumed_short, slave_resumed_short, frame);
    }
}
