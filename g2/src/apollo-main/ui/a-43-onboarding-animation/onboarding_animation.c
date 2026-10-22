/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\onboarding_animation.c
 * (log tag "onboarding.animation"). Native 0x50f8cc..0x50fe79; literal pool
 * 0x50fe7c..0x50fef7; phase config templates ROM 0x762af0/0x762b10/0x762b30/0x762b50.
 *
 * Four frame-sequence animations (common/generic_animation.c) built on the
 * onboarding page, one per tutorial phase, all hidden until shown. The page
 * (ui/a-18-onboarding-main-page) maps an onboarding substep to a phase,
 * stops/hides every phase and ticks the current one. Stock function names come
 * from the log strings where they exist (init, deinit, show_for_substep,
 * show_phase); the TSV has no names, so every function carries its address. */
#include <stdint.h>

#define ONBOARDING_ANIMATION_PHASES 4u
#define LV_OBJ_FLAG_HIDDEN          0x1u
#define LV_ALIGN_LEFT_MID           7u

/* generic_animation_create configuration (ui/a-10-generic-animation). */
typedef struct {
    const void *const *frames; /* +0x00 */
    uint32_t frame_count;      /* +0x04 */
    uint32_t period_ms;        /* +0x08 */
    uint8_t mode;              /* +0x0c 0 loop */
    uint8_t reserved_0d[3];
    int32_t width;             /* +0x10 */
    int32_t height;            /* +0x14 */
    uint8_t color_a[3];        /* +0x18 */
    uint8_t opa_a;             /* +0x1b */
    uint8_t bg_color[3];       /* +0x1c */
    uint8_t bg_opa;            /* +0x1f */
} g2_generic_animation_config_t;
_Static_assert(sizeof(g2_generic_animation_config_t) == 0x20, "stock config is 32 bytes");

struct g2_generic_animation;

/* Onboarding animation configuration, RAM 0x2007345c (built on the stack, then copied). */
typedef struct {
    struct {
        const void *const *frames; /* +0x00 + 8*phase */
        uint32_t frame_count;      /* +0x04 + 8*phase */
    } phase[ONBOARDING_ANIMATION_PHASES];
    uint32_t period_ms;  /* +0x20 50, not used: each phase template sets its own period */
    int32_t width;       /* +0x24 */
    int32_t height;      /* +0x28 */
    uint8_t bg_color[3]; /* +0x2c lv_color_hex(0) */
    uint8_t bg_opa;      /* +0x2f */
} g2_onboarding_animation_config_t;
_Static_assert(sizeof(g2_onboarding_animation_config_t) == 0x30, "stock config is 48 bytes");

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *file, const char *function,
                               uint32_t line, const char *format, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t code, const char *format, const char *text, ...); /* 0x43ce9e */
extern void audio_uart_lv_memzero_48949c(void *destination, uint32_t size);      /* lv_memzero */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);    /* memcpy 0x439be4 */
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);     /* 0x439c04 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);        /* 0x43c0e4 */
extern uint32_t audio_lv_color_44104c(uint32_t rgb);                             /* lv_color_hex */
extern void lv_obj_align_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_lv_object_flag_43ded4(void *obj, uint32_t flag);               /* lv_obj_add_flag */
extern void audio_lv_object_clear_flag_43dfa4(void *obj, uint32_t flag);         /* lv_obj_remove_flag */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *object);             /* lv_obj_is_valid */
extern struct g2_generic_animation *generic_animation_create_463c68(void *parent,
                                                                    const g2_generic_animation_config_t *config);
extern void generic_animation_destroy_463e1c(struct g2_generic_animation *anim, uint8_t delete_image);
extern void *generic_animation_get_image_463e9a(const struct g2_generic_animation *anim);
extern void generic_animation_start_463ea6(struct g2_generic_animation *anim);
extern void generic_animation_stop_463eee(struct g2_generic_animation *anim);
extern void generic_animation_update_463f34(struct g2_generic_animation *anim);

/* Frame tables (arrays of lv_image_dsc_t pointers, initialised RAM data). */
extern const void *const g2_onboarding_anim_frames_0[15]; /* RAM 0x20002e50 */
extern const void *const g2_onboarding_anim_frames_1[35]; /* RAM 0x20002e8c */
extern const void *const g2_onboarding_anim_frames_2[11]; /* RAM 0x20002f18 */
extern const void *const g2_onboarding_anim_frames_3[54]; /* RAM 0x20002f44 */

extern uint8_t g2_onboarding_anim_initialized;      /* RAM 0x20074ff2 */
extern uint8_t g2_onboarding_anim_current_phase;    /* RAM 0x20074ff1 */
extern void *g2_onboarding_anim_parent;             /* RAM 0x2007483c */
extern g2_onboarding_animation_config_t g2_onboarding_anim_config; /* RAM 0x2007345c */
extern struct g2_generic_animation *g2_onboarding_anim_instance[ONBOARDING_ANIMATION_PHASES]; /* RAM 0x20073eb4 */

void onboarding_animation_deinit_50fbb6(void);
int32_t onboarding_animation_show_phase_50fd1a(uint8_t phase);
void onboarding_animation_stop_all_50fe0e(void);

/* Per-phase templates: only period_ms (and mode 0 = loop) are non-zero. */
static const g2_generic_animation_config_t s_phase0_template = {.period_ms = 60u}; /* ROM 0x762af0 */
static const g2_generic_animation_config_t s_phase1_template = {.period_ms = 60u}; /* ROM 0x762b10 */
static const g2_generic_animation_config_t s_phase2_template = {.period_ms = 75u}; /* ROM 0x762b30 */
static const g2_generic_animation_config_t s_phase3_template = {.period_ms = 40u}; /* ROM 0x762b50 */

static const char s_module[] = "onboarding.animation"; /* ROM 0x779cf4 */
static const char s_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\onboarding\\onboarding_animation.c"; /* ROM 0x6eebe8 */
static const char s_init_fn[] = "onboarding_animation_init";       /* ROM 0x76e8f4 */
static const char s_deinit_fn[] = "onboarding_animation_deinit";   /* ROM 0x76e910 */
static const char s_substep_fn[] = "onboarding_animation_show_for_substep"; /* ROM 0x74bd24 */
static const char s_phase_fn[] = "onboarding_animation_show_phase"; /* ROM 0x762ad0 */
static const char s_already[] = "onboarding animation already initialized, not force create"; /* ROM 0x716f24 */
static const char s_already_short[] =
    "[onboarding.animation]onboarding animation already initialized, not force create"; /* ROM 0x6e8e78 */
static const char s_init_ok[] = "Onboarding animation initialized successfully"; /* ROM 0x736164 */
static const char s_init_ok_short[] =
    "[onboarding.animation]Onboarding animation initialized successfully"; /* ROM 0x7044a0 */
static const char s_deinit_ok[] = "Onboarding animation deinitialized"; /* ROM 0x7572e4 */
static const char s_deinit_ok_short[] = "[onboarding.animation]Onboarding animation deinitialized"; /* ROM 0x716f60 */
static const char s_not_init[] = "Animation not initialized"; /* ROM 0x76e92c */
static const char s_not_init_short[] = "[onboarding.animation]Animation not initialized"; /* ROM 0x736194 */
static const char s_no_phase[] = "Animation phase %d does not exist"; /* ROM 0x757308 */
static const char s_no_phase_short[] = "[onboarding.animation]Animation phase %d does not exist"; /* ROM 0x720d70 */
static const char s_showing[] = "Showing animation phase %d"; /* ROM 0x76e948 */
static const char s_showing_short[] = "[onboarding.animation]Showing animation phase %d"; /* ROM 0x72b7e0 */

/* Returns -1 without a parent, 0 otherwise (also when already initialised and
 * force != 1, in which case nothing is rebuilt). */
int32_t onboarding_animation_init_50f8cc(void *parent, uint8_t force)
{
    g2_onboarding_animation_config_t config;
    g2_generic_animation_config_t phase_config0;
    g2_generic_animation_config_t phase_config1;
    g2_generic_animation_config_t phase_config2;
    g2_generic_animation_config_t phase_config3;
    uint32_t color;
    void *image;

    if (parent == 0)
        return -1;

    if (g2_onboarding_anim_initialized != 0u) {
        if (force != 1u) {
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(3u, s_module, s_file, s_init_fn, 95u, s_already);
            if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
                (void)compress_log_output(0x0c000000u, s_already_short, s_already_short);
            return 0;
        }
        onboarding_animation_deinit_50fbb6();
    }

    g2_onboarding_anim_parent = parent;
    audio_uart_lv_memzero_48949c(&config, sizeof(config));
    config.phase[0].frames = g2_onboarding_anim_frames_0;
    config.phase[0].frame_count = 15u;
    config.phase[1].frames = g2_onboarding_anim_frames_1;
    config.phase[1].frame_count = 35u;
    config.phase[2].frames = g2_onboarding_anim_frames_2;
    config.phase[2].frame_count = 11u;
    config.phase[3].frames = g2_onboarding_anim_frames_3;
    config.phase[3].frame_count = 54u;
    config.period_ms = 50u;
    config.width = 24;
    config.height = 24;
    color = audio_lv_color_44104c(0x000000u);
    (void)audio_queue_copy_bytes(config.bg_color, &color, 3u);
    config.bg_opa = 0u;
    (void)audio_queue_copy_bytes(&g2_onboarding_anim_config, &config, sizeof(config));

    if (g2_onboarding_anim_config.phase[0].frames != 0 && g2_onboarding_anim_config.phase[0].frame_count != 0u) {
        (void)aeabi_memcpy4_439c04(&phase_config0, &s_phase0_template, sizeof(phase_config0));
        phase_config0.frames = g2_onboarding_anim_config.phase[0].frames;
        phase_config0.frame_count = g2_onboarding_anim_config.phase[0].frame_count;
        phase_config0.width = g2_onboarding_anim_config.width;
        phase_config0.height = g2_onboarding_anim_config.height;
        (void)audio_queue_copy_bytes(phase_config0.bg_color, g2_onboarding_anim_config.bg_color, 3u);
        phase_config0.bg_opa = g2_onboarding_anim_config.bg_opa;
        g2_onboarding_anim_instance[0] = generic_animation_create_463c68(parent, &phase_config0);
        if (g2_onboarding_anim_instance[0] != 0) {
            image = generic_animation_get_image_463e9a(g2_onboarding_anim_instance[0]);
            if (image != 0) {
                lv_obj_align_43f6b8(image, LV_ALIGN_LEFT_MID, 0, 0);
                audio_lv_object_flag_43ded4(image, LV_OBJ_FLAG_HIDDEN);
            }
        }
    }

    if (g2_onboarding_anim_config.phase[1].frames != 0 && g2_onboarding_anim_config.phase[1].frame_count != 0u) {
        (void)aeabi_memcpy4_439c04(&phase_config1, &s_phase1_template, sizeof(phase_config1));
        phase_config1.frames = g2_onboarding_anim_config.phase[1].frames;
        phase_config1.frame_count = g2_onboarding_anim_config.phase[1].frame_count;
        phase_config1.width = g2_onboarding_anim_config.width;
        phase_config1.height = g2_onboarding_anim_config.height;
        (void)audio_queue_copy_bytes(phase_config1.bg_color, g2_onboarding_anim_config.bg_color, 3u);
        phase_config1.bg_opa = g2_onboarding_anim_config.bg_opa;
        g2_onboarding_anim_instance[1] = generic_animation_create_463c68(parent, &phase_config1);
        if (g2_onboarding_anim_instance[1] != 0) {
            image = generic_animation_get_image_463e9a(g2_onboarding_anim_instance[1]);
            if (image != 0) {
                lv_obj_align_43f6b8(image, LV_ALIGN_LEFT_MID, 0, 0);
                audio_lv_object_flag_43ded4(image, LV_OBJ_FLAG_HIDDEN);
            }
        }
    }

    if (g2_onboarding_anim_config.phase[2].frames != 0 && g2_onboarding_anim_config.phase[2].frame_count != 0u) {
        (void)aeabi_memcpy4_439c04(&phase_config2, &s_phase2_template, sizeof(phase_config2));
        phase_config2.frames = g2_onboarding_anim_config.phase[2].frames;
        phase_config2.frame_count = g2_onboarding_anim_config.phase[2].frame_count;
        phase_config2.width = g2_onboarding_anim_config.width;
        phase_config2.height = g2_onboarding_anim_config.height;
        (void)audio_queue_copy_bytes(phase_config2.bg_color, g2_onboarding_anim_config.bg_color, 3u);
        phase_config2.bg_opa = g2_onboarding_anim_config.bg_opa;
        g2_onboarding_anim_instance[2] = generic_animation_create_463c68(parent, &phase_config2);
        if (g2_onboarding_anim_instance[2] != 0) {
            image = generic_animation_get_image_463e9a(g2_onboarding_anim_instance[2]);
            if (image != 0) {
                lv_obj_align_43f6b8(image, LV_ALIGN_LEFT_MID, 0, 0);
                audio_lv_object_flag_43ded4(image, LV_OBJ_FLAG_HIDDEN);
            }
        }
    }

    if (g2_onboarding_anim_config.phase[3].frames != 0 && g2_onboarding_anim_config.phase[3].frame_count != 0u) {
        (void)aeabi_memcpy4_439c04(&phase_config3, &s_phase3_template, sizeof(phase_config3));
        phase_config3.frames = g2_onboarding_anim_config.phase[3].frames;
        phase_config3.frame_count = g2_onboarding_anim_config.phase[3].frame_count;
        phase_config3.width = g2_onboarding_anim_config.width;
        phase_config3.height = g2_onboarding_anim_config.height;
        (void)audio_queue_copy_bytes(phase_config3.bg_color, g2_onboarding_anim_config.bg_color, 3u);
        phase_config3.bg_opa = g2_onboarding_anim_config.bg_opa;
        g2_onboarding_anim_instance[3] = generic_animation_create_463c68(parent, &phase_config3);
        if (g2_onboarding_anim_instance[3] != 0) {
            image = generic_animation_get_image_463e9a(g2_onboarding_anim_instance[3]);
            if (image != 0) {
                lv_obj_align_43f6b8(image, LV_ALIGN_LEFT_MID, 0, 0);
                audio_lv_object_flag_43ded4(image, LV_OBJ_FLAG_HIDDEN);
            }
        }
    }

    g2_onboarding_anim_initialized = 1u;
    g2_onboarding_anim_current_phase = 0u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, s_module, s_file, s_init_fn, 215u, s_init_ok);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x0c000000u, s_init_ok_short, s_init_ok_short);
    return 0;
}

/* Destroys the animations but keeps their image objects (delete_image = 0);
 * the page deletes its children itself. */
void onboarding_animation_deinit_50fbb6(void)
{
    if (g2_onboarding_anim_initialized == 0u)
        return;

    for (int32_t i = 0; i < (int32_t)ONBOARDING_ANIMATION_PHASES; i++) {
        if (g2_onboarding_anim_instance[i] != 0) {
            generic_animation_destroy_463e1c(g2_onboarding_anim_instance[i], 0u);
            g2_onboarding_anim_instance[i] = 0;
        }
    }
    (void)aeabi_memset_43c0e4(&g2_onboarding_anim_config, sizeof(g2_onboarding_anim_config), 0);
    g2_onboarding_anim_parent = 0;
    g2_onboarding_anim_initialized = 0u;
    g2_onboarding_anim_current_phase = 0u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, s_module, s_file, s_deinit_fn, 238u, s_deinit_ok);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x0c000000u, s_deinit_ok_short, s_deinit_ok_short);
}

/* Image object of one phase, or NULL (called once, right after init, from the
 * welcome-view create code at 0x4aaf80). */
void *onboarding_animation_get_phase_image_50fc4e(uint8_t phase)
{
    if (g2_onboarding_anim_initialized == 0u || phase >= ONBOARDING_ANIMATION_PHASES)
        return 0;
    if (g2_onboarding_anim_instance[phase] == 0)
        return 0;
    return generic_animation_get_image_463e9a(g2_onboarding_anim_instance[phase]);
}

/* Substeps 0/6/11/13 -> phase 0, 2 -> 1, 4 -> 2, 8 -> 3; other substeps -1. */
int32_t onboarding_animation_show_for_substep_50fc86(uint8_t substep)
{
    uint8_t phase;

    if (g2_onboarding_anim_initialized == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, s_module, s_file, s_substep_fn, 257u, s_not_init);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compress_log_output(0x08000000u, s_not_init_short, s_not_init_short);
        return -1;
    }

    switch (substep) {
    case 0u:  phase = 0u; break;
    case 2u:  phase = 1u; break;
    case 4u:  phase = 2u; break;
    case 6u:  phase = 0u; break;
    case 8u:  phase = 3u; break;
    case 11u: phase = 0u; break;
    case 13u: phase = 0u; break;
    default:  return -1;
    }
    return onboarding_animation_show_phase_50fd1a(phase);
}

/* Hides and stops every phase, then unhides and starts the requested one. */
int32_t onboarding_animation_show_phase_50fd1a(uint8_t phase)
{
    void *image;

    if (g2_onboarding_anim_initialized == 0u || phase >= ONBOARDING_ANIMATION_PHASES)
        return -1;

    if (g2_onboarding_anim_instance[phase] == 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, s_module, s_file, s_phase_fn, 315u, s_no_phase, phase);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compress_log_output(0x04400000u, s_no_phase_short, s_no_phase_short, phase);
        return -1;
    }

    onboarding_animation_stop_all_50fe0e();
    image = generic_animation_get_image_463e9a(g2_onboarding_anim_instance[phase]);
    if (image != 0 && audio_terminal_ui_object_valid_43e2ea(image) != 0u)
        audio_lv_object_clear_flag_43dfa4(image, LV_OBJ_FLAG_HIDDEN);
    generic_animation_start_463ea6(g2_onboarding_anim_instance[phase]);
    g2_onboarding_anim_current_phase = phase;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, s_module, s_file, s_phase_fn, 340u, s_showing, phase);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10400000u, s_showing_short, s_showing_short, phase);
    return 0;
}

void onboarding_animation_stop_all_50fe0e(void)
{
    void *image;

    if (g2_onboarding_anim_initialized == 0u)
        return;

    for (int32_t i = 0; i < (int32_t)ONBOARDING_ANIMATION_PHASES; i++) {
        if (g2_onboarding_anim_instance[i] != 0) {
            generic_animation_stop_463eee(g2_onboarding_anim_instance[i]);
            image = generic_animation_get_image_463e9a(g2_onboarding_anim_instance[i]);
            if (image != 0 && audio_terminal_ui_object_valid_43e2ea(image) != 0u)
                audio_lv_object_flag_43ded4(image, LV_OBJ_FLAG_HIDDEN);
        }
    }
}

/* Advances the current phase; called from the page timer. */
void onboarding_animation_tick_50fe56(void)
{
    if (g2_onboarding_anim_initialized == 0u)
        return;
    if (g2_onboarding_anim_instance[g2_onboarding_anim_current_phase] != 0)
        generic_animation_update_463f34(g2_onboarding_anim_instance[g2_onboarding_anim_current_phase]);
}
