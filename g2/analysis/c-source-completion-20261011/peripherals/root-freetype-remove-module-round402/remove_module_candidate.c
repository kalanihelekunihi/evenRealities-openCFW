#include <stdint.h>

extern void audio_uart_font_mem_free(void *, void *);
extern uint32_t audio_uart_ft_remove_renderer_52716c(void *);
extern uint32_t audio_uart_ft_destroy_driver_525936(void *);

static uint32_t ft402_word(const void *base, uint32_t offset)
{
    return *(const volatile uint32_t *)((uintptr_t)base + offset);
}

static void ft402_set_word(void *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)((uintptr_t)base + offset) = value;
}

/* Whole native FT_Done_Module body at 0x52724c, 80 bytes. */
uint32_t audio_uart_ft_done_module_52724c(void *module)
{
    const void *clazz = (const void *)(uintptr_t)ft402_word(module, 0u);
    void *library = (void *)(uintptr_t)ft402_word(module, 4u);
    void *memory = (void *)(uintptr_t)ft402_word(module, 8u);
    if (library != 0 && ft402_word(library, 0xa0u) == (uint32_t)(uintptr_t)module)
        ft402_set_word(library, 0xa0u, 0u);
    uint32_t flags = ft402_word(clazz, 0u);
    if ((flags & 2u) != 0u) (void)audio_uart_ft_remove_renderer_52716c(module);
    if ((flags & 1u) != 0u) (void)audio_uart_ft_destroy_driver_525936(module);
    uint32_t done = ft402_word(clazz, 28u);
    if (done != 0u) ((void (*)(void *))(uintptr_t)done)(module);
    audio_uart_font_mem_free(memory, module);
    return 0u;
}

/* Whole native FT_Remove_Module body at 0x527466, 76 bytes. */
uint32_t audio_uart_ft_remove_module_527466(void *library, void *module)
{
    if (library == 0) return 0x21u;
    if (module != 0) {
        uint32_t count = ft402_word(library, 16u);
        for (uint32_t i = 0; i < count; ++i) {
            if (ft402_word(library, 20u + i * 4u) == (uint32_t)(uintptr_t)module) {
                ft402_set_word(library, 16u, count - 1u);
                for (uint32_t j = i; j + 1u < count; ++j)
                    ft402_set_word(library, 20u + j * 4u,
                                   ft402_word(library, 20u + (j + 1u) * 4u));
                ft402_set_word(library, 20u + (count - 1u) * 4u, 0u);
                (void)audio_uart_ft_done_module_52724c(module);
                return 0u;
            }
        }
    }
    return 0x22u;
}
