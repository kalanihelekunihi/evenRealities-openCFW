#include <stdint.h>

extern void *audio_uart_font_mem_alloc(void *, int32_t, int32_t *);
extern void audio_uart_font_mem_free(void *, void *);
extern void audio_uart_ft_list_add_529304(void *, void *);
extern void *audio_uart_ft_list_find_5292e6(void *, void *);
extern void audio_uart_ft_list_remove_529324(void *, void *);
extern void *audio_uart_font_lookup_renderer(void *, uint32_t, void *);

static uint32_t ft403_word(const void *base, uint32_t offset)
{
    return *(const volatile uint32_t *)((uintptr_t)base + offset);
}

static void ft403_set_word(void *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)((uintptr_t)base + offset) = value;
}

/* Whole native ft_set_current_renderer body at 0x5270bc, 22 bytes. */
void audio_uart_ft_set_current_renderer_5270bc(void *library)
{
    void *renderer = audio_uart_font_lookup_renderer(library, 0x6f75746cu, 0);
    ft403_set_word(library, 0x9cu, (uint32_t)(uintptr_t)renderer);
}

/* Whole native ft_add_renderer body at 0x5270d2, 154 bytes. */
uint32_t audio_uart_ft_add_renderer_5270d2(void *module)
{
    void *library = (void *)(uintptr_t)ft403_word(module, 4u);
    void *memory = (void *)(uintptr_t)ft403_word(library, 0u);
    int32_t error = 0;
    void *node = audio_uart_font_mem_alloc(memory, 12, &error);
    if (error != 0) return (uint32_t)error;

    const void *clazz = (const void *)(uintptr_t)ft403_word(module, 0u);
    ft403_set_word(module, 12u, (uint32_t)(uintptr_t)clazz);
    uint32_t glyph_format = ft403_word(clazz, 36u);
    ft403_set_word(module, 16u, glyph_format);
    if (glyph_format == 0x6f75746cu) {
        const void *raster_class = (const void *)(uintptr_t)ft403_word(clazz, 56u);
        uint32_t raster_new = ft403_word(raster_class, 4u);
        if (raster_new != 0u) {
            error = ((int32_t (*)(void *, void **))(uintptr_t)raster_new)(
                memory, (void **)((uintptr_t)module + 52u));
            if (error != 0) goto fail;
            ft403_set_word(module, 56u, ft403_word(raster_class, 16u));
            ft403_set_word(module, 60u, ft403_word(clazz, 40u));
        }
    }
    ft403_set_word(node, 8u, (uint32_t)(uintptr_t)module);
    audio_uart_ft_list_add_529304((void *)((uintptr_t)library + 0x94u), node);
    audio_uart_ft_set_current_renderer_5270bc(library);
    return (uint32_t)error;

fail:
    audio_uart_font_mem_free(memory, node);
    return (uint32_t)error;
}

/* Whole native ft_remove_renderer body at 0x52716c, 84 bytes. */
void audio_uart_ft_remove_renderer_52716c(void *module)
{
    void *library = (void *)(uintptr_t)ft403_word(module, 4u);
    if (library == 0) return;
    void *memory = (void *)(uintptr_t)ft403_word(library, 0u);
    void *list = (void *)((uintptr_t)library + 0x94u);
    void *node = audio_uart_ft_list_find_5292e6(list, module);
    if (node == 0) return;
    const void *clazz = (const void *)(uintptr_t)ft403_word(module, 12u);
    if (ft403_word(clazz, 36u) == 0x6f75746cu && ft403_word(module, 52u) != 0u) {
        const void *raster_class = (const void *)(uintptr_t)ft403_word(clazz, 56u);
        uint32_t raster_done = ft403_word(raster_class, 20u);
        ((void (*)(void *))(uintptr_t)raster_done)(
            (void *)(uintptr_t)ft403_word(module, 52u));
    }
    audio_uart_ft_list_remove_529324(list, node);
    audio_uart_font_mem_free(memory, node);
    audio_uart_ft_set_current_renderer_5270bc(library);
}
