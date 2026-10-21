/* Stock semantic_production_test_screen_event at 0x5cf7f2.
 * The C-owned root cell corresponds to native RAM 0x20074894.  The page
 * registry context at 0x200030a0 is supplied by the existing registry. */
#include <stdint.h>

uint32_t audio_uart_production_test_root_20074894;

extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern void audio_uart_page_43f506(uint32_t, uint32_t);
extern void audio_uart_page_43f568(uint32_t, uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, int32_t, int32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44127e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_4412ec(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_441068(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_registry_context_200030a0[];

uint64_t audio_uart_registry_callback_5cf7f2(uint32_t event,
                                               uint32_t arg2,
                                               uint32_t arg3,
                                               uint32_t parent) {
    (void)arg2;
    (void)arg3;
    uint32_t upper = parent;
    if (event == 2u) {
        uint32_t root = audio_uart_page_43de82(parent);
        audio_uart_production_test_root_20074894 = root;
        audio_uart_page_43dfa4(root, 0x10u);
        audio_uart_page_43f506(root, 0x280u);
        audio_uart_page_43f568(root, 0x1e0u);
        audio_uart_page_43dfa4(root, 0x10u);
        audio_uart_page_44127e(root, audio_uart_page_44104c(0u), 0u);
        audio_uart_page_44129e(root, 0xffu, 0u);
        upper = parent & 0xff000000u;
        audio_uart_page_4412ec(root, upper, 0u);
        for (uint32_t row = 0; row < 3u; ++row) {
            for (uint32_t column = 0; column < 3u; ++column) {
                uint32_t tile = audio_uart_page_43de82(root);
                audio_uart_page_43f4c0(tile, 10u, 10u);
                audio_uart_page_44127e(tile,
                                       audio_uart_page_441068(0xffu, 0xffu, 0xffu), 0u);
                audio_uart_page_44131c(tile, 0u, 0u);
                audio_uart_page_43f09a(tile, (int32_t)(column * 200u + 0x42u),
                                       (int32_t)(row * 100u + 0x15u));
            }
        }
        audio_uart_registry_context_200030a0[1] = root;
    }
    return (uint64_t)upper << 32;
}
