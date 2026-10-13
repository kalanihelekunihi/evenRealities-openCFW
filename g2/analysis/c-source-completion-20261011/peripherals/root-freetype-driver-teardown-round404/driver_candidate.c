#include <stdint.h>

extern void audio_uart_ft_list_finalize_529378(void *, void (*)(void *, void *, void *), void *, void *);
extern void audio_uart_ft_destroy_face_5258a8(void *, void *, void *);

/* Whole native driver teardown at 0x525936, 20 bytes. */
void audio_uart_ft_destroy_driver_525936(void *driver)
{
    void *memory = (void *)(uintptr_t)*(const volatile uint32_t *)((uintptr_t)driver + 8u);
    audio_uart_ft_list_finalize_529378((void *)((uintptr_t)driver + 16u),
                                       audio_uart_ft_destroy_face_5258a8,
                                       memory, driver);
}
