/* Native semantic_pdt_gray_screen_event 0x5cf67e..0x5cf787.
 * The eight grayscale steps are from stock ROM 0x0078df8c. */
#include <stdint.h>

uint32_t audio_uart_gray_screen_root_20074880;
const uint8_t audio_uart_gray_screen_steps_78df8c[8] =
    {1u, 2u, 4u, 8u, 8u, 4u, 2u, 1u};

extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern void audio_uart_page_43f506(uint32_t, uint32_t);
extern void audio_uart_page_43f568(uint32_t, uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, int32_t, int32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern uint32_t audio_uart_page_441068(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44127e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_4412ec(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_registry_context_20003080[];

uint64_t audio_uart_registry_callback_5cf67e(uint32_t event,
                                               uint32_t arg2,
                                               uint32_t value,
                                               uint32_t parent) {
    (void)arg2;
    uint32_t upper = value;
    if (event == 2u) {
        uint32_t root = audio_uart_page_43de82(parent);
        audio_uart_gray_screen_root_20074880 = root;
        audio_uart_page_43dfa4(root, 0x10u);
        audio_uart_page_43f506(root, 0x280u);
        audio_uart_page_43f568(root, 0x1e0u);
        audio_uart_page_43dfa4(root, 0x10u);
        audio_uart_page_44127e(root, audio_uart_page_44104c(0u), 0u);
        audio_uart_page_44129e(root, 0xffu, 0u);
        upper = value & 0xff000000u;
        audio_uart_page_4412ec(root, upper, 0u);
        for (uint32_t index = 0; index < 8u; ++index) {
            uint32_t tile = audio_uart_page_43de82(root);
            audio_uart_page_43dfa4(tile, 0x10u);
            audio_uart_page_43f4c0(tile, 0x48u, 0x120u);
            audio_uart_page_43f09a(tile, (int32_t)(index * 0x48u), 0);
            audio_uart_page_44131c(tile, 0u, 0u);
            audio_uart_page_44146a(tile, 0u, 0u);
            uint32_t gray = (uint8_t)(audio_uart_gray_screen_steps_78df8c[index] * 0x11u);
            audio_uart_page_44127e(tile, audio_uart_page_441068(gray, gray, gray), 0u);
            audio_uart_page_44129e(tile, 0xffu, 0u);
        }
        audio_uart_registry_context_20003080[1] = root;
    }
    return (uint64_t)upper << 32;
}
