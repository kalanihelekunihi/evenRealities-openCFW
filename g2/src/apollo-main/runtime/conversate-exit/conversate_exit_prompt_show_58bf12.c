/* Native exit-prompt step-one display at 0x58bf12. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t level, const char *module,
                               const char *path, const char *function,
                               uint32_t line, const char *format, ...);
extern uint32_t compressed_log_output(uint32_t mask, const char *format,
                                      const char *copy, ...);
extern uint32_t audio_conversate_exit_prompt_state_200745d0[3];
extern uint32_t audio_uart_ring_primary_head_cell;
extern void audio_uart_page_44d878(void *object);
extern void *audio_uart_page_499416(void *parent);
extern void audio_uart_page_43f4c0(void *object, uint32_t width, uint32_t height);
extern void audio_uart_page_43f6b8(void *object, uint32_t selector,
                                   uint32_t value, uint32_t part);
extern void audio_uart_page_49942e(void *label, const char *text);
extern void audio_uart_page_44143e(void *label, uint32_t font, uint32_t part);
extern uint32_t audio_uart_page_44104c(uint32_t rgb);
extern void audio_uart_page_44140e(void *label, uint32_t color, uint32_t part);
extern void audio_uart_page_44145a(void *label, uint32_t value, uint32_t part);
extern void audio_uart_page_58c238(uint32_t object, uint32_t duration,
                                   uint32_t complete);
extern void audio_conversate_exit_prompt_fade_step_58bebc(void);

static const char module[] = "exit_prompt";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\exit_prompt.c";
static const char function[] = "common_exit_prompt_fade_cb_step1";
static const char step[] = "step 1";
static const char compact[] = "[exit_prompt]step 1";

void audio_conversate_exit_prompt_show_58bf12(void) {
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x3du, step);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c000000u, compact, compact);
    const uint32_t app = audio_conversate_exit_prompt_state_200745d0[0];
    audio_uart_page_44d878((void *)(uintptr_t)app);
    void *const label = audio_uart_page_499416((void *)(uintptr_t)app);
    audio_uart_page_43f4c0(label, 0x3fffffffu, 0x3fffffffu);
    audio_uart_page_43f6b8(label, 9u, 0u, 0u);
    audio_uart_page_49942e(label, (const char *)(uintptr_t)
                            audio_conversate_exit_prompt_state_200745d0[1]);
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0x00ffffffu), 0u);
    audio_uart_page_44145a(label, 2u, 0u);
    audio_uart_page_58c238(app, 250u,
                            (uint32_t)(uintptr_t)
                            audio_conversate_exit_prompt_fade_step_58bebc);
}
