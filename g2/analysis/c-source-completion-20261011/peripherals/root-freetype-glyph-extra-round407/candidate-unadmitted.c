#include <stdint.h>

/* Native 0x524c3a..0x524c88, pinned FreeType 2.9.1 ftgloadr.c. */
static uint32_t ft407_word(const void *base, uint32_t offset) {
  const uint8_t *p = (const uint8_t *)base + offset;
  return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
         ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
static void ft407_store(void *base, uint32_t offset, uint32_t value) {
  uint8_t *p = (uint8_t *)base + offset;
  p[0] = (uint8_t)value;
  p[1] = (uint8_t)(value >> 8);
  p[2] = (uint8_t)(value >> 16);
  p[3] = (uint8_t)(value >> 24);
}
static int32_t ft407_short(const void *base, uint32_t offset) {
  const uint8_t *p = (const uint8_t *)base + offset;
  return (int16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

void audio_uart_ft_glyph_loader_adjust_points_524c3a(void *loader) {
  int32_t points = ft407_short(loader, 22u);
  int32_t contours = ft407_short(loader, 20u);
  ft407_store(loader, 60u, ft407_word(loader, 24u) + (uint32_t)(points * 8));
  ft407_store(loader, 64u, ft407_word(loader, 28u) + (uint32_t)points);
  ft407_store(loader, 68u, ft407_word(loader, 32u) + (uint32_t)(contours * 2));
  if (((uint8_t *)loader)[16u] != 0u) {
    ft407_store(loader, 76u, ft407_word(loader, 40u) + (uint32_t)(points * 8));
    ft407_store(loader, 80u, ft407_word(loader, 44u) + (uint32_t)(points * 8));
  }
}

/* Native 0x524c88..0x524cc4. The qalloc child is still a controlled import. */
extern void *audio_uart_ft_mem_qalloc_52919c(void *, uint32_t, uint32_t,
                                                uint32_t, void *, int32_t *);
uint32_t audio_uart_ft_glyph_loader_create_extra_524c88(void *loader) {
  int32_t error = 0;
  uint32_t max_points = ft407_word(loader, 4u);
  void *extra = audio_uart_ft_mem_qalloc_52919c(
      (void *)(uintptr_t)ft407_word(loader, 0u), 8u, 0u,
      max_points * 2u, (void *)0, &error);
  ft407_store(loader, 40u, (uint32_t)(uintptr_t)extra);
  if (error == 0) {
    ((uint8_t *)loader)[16u] = 1u;
    ft407_store(loader, 44u, (uint32_t)(uintptr_t)extra + max_points * 8u);
    audio_uart_ft_glyph_loader_adjust_points_524c3a(loader);
  }
  return (uint32_t)error;
}
