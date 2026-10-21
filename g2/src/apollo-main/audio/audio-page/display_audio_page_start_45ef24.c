/* Apollo audio display animation start, stock 0x45ef24..0x45f159. */
#include <stdint.h>

extern void audio_uart_lv_anim_init_4503d6(void *);
extern void audio_uart_lv_anim_values_4506ce(void *, int32_t, int32_t);
extern void audio_uart_lv_anim_start_450408(void *);
extern void *audio_uart_display_audio_find_owner_45fcd2(void *);
extern void audio_uart_display_audio_prepare_45bbb6(void);
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern int32_t audio_uart_lv_obj_x_43fc70(void *);
extern int32_t audio_uart_lv_obj_y_43fce0(void *);
extern void audio_uart_page_43f0e0(uint32_t, uint32_t);
extern void audio_uart_page_43f142(uint32_t, uint32_t);
extern void audio_uart_display_audio_reset_441488(uint32_t, uint32_t, uint32_t);
extern void audio_uart_display_anim_x_a_45ecaf(void);
extern void audio_uart_display_anim_y_a_45ecb7(void);
extern void audio_uart_display_anim_alpha_45ecbf(void);
extern void audio_uart_display_anim_finish_b_45ed4f(void);
extern void audio_uart_display_anim_finish_a_45ee35(void);
extern void audio_uart_display_anim_finish_c_45eccb(void);
extern void audio_uart_display_anim_finish_d_45ed91(void);

typedef struct { uint32_t words[24]; } audio_anim_descriptor;

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static int32_t scaled(int32_t value, int32_t percent) {
    uint32_t product = (uint32_t)value * (uint32_t)(100 - percent);
    return (int32_t)product / 100;
}

void audio_uart_display_audio_start_45ef24(void *entry, uint32_t forward) {
    const uint8_t *e = (const uint8_t *)entry;
    audio_anim_descriptor animation;
    audio_uart_lv_anim_init_4503d6(&animation);
    uint32_t page = get32(e + 4u);
    animation.words[0] = page;
    uint8_t alpha_mode = e[10];
    uint8_t direction = alpha_mode ? e[9] : e[8];
    animation.words[12] = get32(e + (alpha_mode ? 16u : 12u));
    uint8_t *owner = (uint8_t *)audio_uart_display_audio_find_owner_45fcd2(
        (void *)(uintptr_t)page);
    if (owner != 0) owner[0xe8u] = 1u;
    audio_uart_display_audio_prepare_45bbb6();
    int32_t percent = (int16_t)((uint16_t)e[20] | ((uint16_t)e[21] << 8u));
    int32_t from = 0;
    int32_t to = 0;
    if (alpha_mode != 0u) {
        void *parent = audio_uart_lv_obj_parent_44dca2((void *)(uintptr_t)page);
        int32_t extent = direction == 0u ?
            audio_uart_lv_obj_width_43fd9e(parent) :
            audio_uart_lv_obj_height_43fdda(parent);
        to = scaled(extent, percent);
        animation.words[4] = (uint32_t)(uintptr_t)audio_uart_display_anim_alpha_45ecbf;
        if ((uint8_t)forward == 0u) {
            animation.words[1] = (uint32_t)(uintptr_t)audio_uart_display_anim_alpha_45ecbf;
            audio_uart_lv_anim_values_4506ce(&animation, 255, 0);
            animation.words[4] = (uint32_t)(uintptr_t)(e[11] == 1u ?
                audio_uart_display_anim_finish_a_45ee35 :
                audio_uart_display_anim_finish_c_45eccb);
        } else {
            if (direction == 0u)
                audio_uart_page_43f0e0(page, (uint32_t)to);
            else
                audio_uart_page_43f142(page, (uint32_t)to);
            audio_uart_display_audio_reset_441488(page, 0u, 0u);
            animation.words[1] = (uint32_t)(uintptr_t)audio_uart_display_anim_alpha_45ecbf;
            audio_uart_lv_anim_values_4506ce(&animation, 0, 255);
            animation.words[4] = (uint32_t)(uintptr_t)audio_uart_display_anim_finish_b_45ed4f;
        }
    } else {
        void *parent = audio_uart_lv_obj_parent_44dca2((void *)(uintptr_t)page);
        int32_t extent = direction == 0u ?
            audio_uart_lv_obj_width_43fd9e(parent) :
            audio_uart_lv_obj_height_43fdda(parent);
        animation.words[1] = (uint32_t)(uintptr_t)(direction == 0u ?
            audio_uart_display_anim_x_a_45ecaf :
            audio_uart_display_anim_y_a_45ecb7);
        if ((uint8_t)forward == 0u) {
            from = direction == 0u ?
                audio_uart_lv_obj_x_43fc70((void *)(uintptr_t)page) :
                audio_uart_lv_obj_y_43fce0((void *)(uintptr_t)page);
            to = direction == 1u ? extent :
                -(direction == 0u ?
                    audio_uart_lv_obj_width_43fd9e((void *)(uintptr_t)page) :
                    audio_uart_lv_obj_height_43fdda((void *)(uintptr_t)page));
        } else {
            from = direction == 1u ? extent :
                -(direction == 0u ?
                    audio_uart_lv_obj_width_43fd9e((void *)(uintptr_t)page) :
                    audio_uart_lv_obj_height_43fdda((void *)(uintptr_t)page));
            to = scaled(extent, percent);
        }
        audio_uart_lv_anim_values_4506ce(&animation, from, to);
        animation.words[4] = (uint32_t)(uintptr_t)((uint8_t)forward == 0u && e[11] == 1u ?
            audio_uart_display_anim_finish_d_45ed91 :
            audio_uart_display_anim_finish_c_45eccb);
    }
    audio_uart_lv_anim_start_450408(&animation);
}
