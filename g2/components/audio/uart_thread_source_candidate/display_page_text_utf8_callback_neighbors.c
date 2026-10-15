/* Apollo LV UTF-8 ROM callback table neighbors around cell 0x78f2a4.
 * Native table 0x78f29c..0x78f2b7 has seven Thumb function pointers. */
#include <stdint.h>

extern uint32_t audio_uart_text_utf8_length_489b74(const char *text);
extern uint32_t audio_uart_text_utf8_encode_489bac(uint32_t glyph);
extern uint64_t audio_uart_text_utf8_previous_489dbc(const char *text,
                                                      uint32_t *offset,
                                                      uint32_t fallback_high,
                                                      uint32_t unused);
extern uint64_t audio_uart_text_utf8_bytes_for_count_489e14(const char *text,
                                                              uint32_t count,
                                                              uint32_t unused,
                                                              uint32_t high);
extern uint64_t audio_uart_text_utf8_count_to_bytes_489e4a(const char *text,
                                                             uint32_t bytes,
                                                             uint32_t high,
                                                             uint32_t unused);
extern uint64_t audio_uart_text_utf8_count_489e6e(const char *text,
                                                   uint32_t unused1,
                                                   uint32_t unused2,
                                                   uint32_t high);

const uintptr_t audio_uart_text_utf8_callback_prefix_78f29c[2]
    __attribute__((section(".g2_rom_78f29c"), used)) = {
        (uintptr_t)&audio_uart_text_utf8_length_489b74,
        (uintptr_t)&audio_uart_text_utf8_encode_489bac,
};

const uintptr_t audio_uart_text_utf8_callback_suffix_78f2a8[4]
    __attribute__((section(".g2_rom_78f2a8"), used)) = {
        (uintptr_t)&audio_uart_text_utf8_previous_489dbc,
        (uintptr_t)&audio_uart_text_utf8_bytes_for_count_489e14,
        (uintptr_t)&audio_uart_text_utf8_count_to_bytes_489e4a,
        (uintptr_t)&audio_uart_text_utf8_count_489e6e,
};
