#include <stdint.h>

extern int32_t audio_uart_font_path_compare(const char *, const char *);
extern void *audio_uart_font_mem_alloc(void *, int32_t, int32_t *);
extern void audio_uart_font_mem_free(void *, void *);
extern uint32_t audio_uart_ft_remove_module_527466(void *, void *);
extern uint32_t audio_uart_ft_add_renderer_5270d2(void *);

static uint32_t ft401_word(const void *base, uint32_t offset)
{
    return *(const volatile uint32_t *)((uintptr_t)base + offset);
}

static void ft401_set_word(void *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)((uintptr_t)base + offset) = value;
}

/* Whole native FT_Add_Module body at 0x52729c, 278 bytes. */
uint32_t audio_uart_ft_add_module_52729c(void *library, const void *clazz)
{
    if (library == 0) return 0x21u;
    if (clazz == 0) return 6u;
    if ((int32_t)ft401_word(clazz, 16u) >= 0x2000a) return 4u;

    for (uint32_t i = 0; i < ft401_word(library, 16u); ++i) {
        void *existing = (void *)(uintptr_t)ft401_word(library, 20u + i * 4u);
        const void *old_class = (const void *)(uintptr_t)ft401_word(existing, 0u);
        if (audio_uart_font_path_compare(
                (const char *)(uintptr_t)ft401_word(old_class, 8u),
                (const char *)(uintptr_t)ft401_word(clazz, 8u)) == 0) {
            if ((int32_t)ft401_word(clazz, 12u) <= (int32_t)ft401_word(old_class, 12u))
                return 5u;
            (void)audio_uart_ft_remove_module_527466(library, existing);
            break;
        }
    }

    void *memory = (void *)(uintptr_t)ft401_word(library, 0u);
    int32_t error = 0;
    if (ft401_word(library, 16u) >= 32u) return 0x30u;

    void *module = audio_uart_font_mem_alloc(memory, (int32_t)ft401_word(clazz, 4u), &error);
    if (error != 0) return (uint32_t)error;
    ft401_set_word(module, 4u, (uint32_t)(uintptr_t)library);
    ft401_set_word(module, 8u, (uint32_t)(uintptr_t)memory);
    ft401_set_word(module, 0u, (uint32_t)(uintptr_t)clazz);

    uint32_t flags = ft401_word(clazz, 0u);
    if ((flags & 2u) != 0u) {
        error = (int32_t)audio_uart_ft_add_renderer_5270d2(module);
        if (error != 0) goto fail;
    }
    if ((flags & 4u) != 0u) ft401_set_word(library, 0xa0u, (uint32_t)(uintptr_t)module);
    if ((flags & 1u) != 0u) ft401_set_word(module, 12u, (uint32_t)(uintptr_t)clazz);

    uint32_t init = ft401_word(clazz, 24u);
    if (init != 0u) {
        error = ((int32_t (*)(void *))(uintptr_t)init)(module);
        if (error != 0) goto fail;
    }
    uint32_t count = ft401_word(library, 16u);
    ft401_set_word(library, 16u, count + 1u);
    ft401_set_word(library, 20u + count * 4u, (uint32_t)(uintptr_t)module);
    return (uint32_t)error;

fail:
    if ((flags & 2u) != 0u) {
        const void *renderer_class = (const void *)(uintptr_t)ft401_word(module, 12u);
        if (renderer_class != 0 && ft401_word(renderer_class, 36u) == 0x6f75746cu &&
            ft401_word(module, 52u) != 0u) {
            const void *raster_class = (const void *)(uintptr_t)ft401_word(renderer_class, 56u);
            uint32_t raster_done = ft401_word(raster_class, 20u);
            ((void (*)(void *))(uintptr_t)raster_done)((void *)(uintptr_t)ft401_word(module, 52u));
        }
    }
    audio_uart_font_mem_free(memory, module);
    return (uint32_t)error;
}
