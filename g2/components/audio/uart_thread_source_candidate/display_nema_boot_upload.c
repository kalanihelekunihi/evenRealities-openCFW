/* Apollo MAIN s200 v2.2.6.10 native 0x5138a4 boot instruction upload.
 * Six words at ROM 0x513ea8..0x513ebf are copied to a local buffer.
 * State at native RAM 0x200043a8 has authenticated initial bytes
 * 00 00 00 00 00 80 00 00. Final placement remains a linker gate. */
#include <stddef.h>
#include <stdint.h>

extern void audio_uart_nema_instruction_upload_522920(const uint32_t *, uint32_t, uint32_t);
extern uint32_t audio_uart_nema_child_522602(void);
extern void audio_uart_nema_rop_blend_mode_522956(uint32_t);

struct audio_uart_nema_boot_state {
    volatile uint8_t mode_flag;
    uint8_t reserved[3];
    volatile uint32_t word;
};
struct audio_uart_nema_boot_state audio_uart_nema_boot_state_200043a8 = {
    .word = 0x8000u,
};
_Static_assert(sizeof(struct audio_uart_nema_boot_state) == 8u,
               "Nema boot state extent");
_Static_assert(offsetof(struct audio_uart_nema_boot_state, word) == 4u,
               "Nema boot state word offset");

void audio_uart_nema_child_5138a4(void) {
    uint32_t words[6] = {0u, 0u, 0x08000002u, 0x80000009u, 0u, 0u};
    for (uint32_t address = 0x18u; address <= 0x1eu; ++address)
        audio_uart_nema_instruction_upload_522920(words, 1u, address);
    audio_uart_nema_instruction_upload_522920(words + 2, 1u, 0x1fu);
    uint8_t bit = (uint8_t)((audio_uart_nema_child_522602() >> 28) & 1u);
    audio_uart_nema_boot_state_200043a8.mode_flag = bit;
    if (bit != 0u) {
        audio_uart_nema_boot_state_200043a8.word = 0u;
        audio_uart_nema_rop_blend_mode_522956(1u);
    }
}
