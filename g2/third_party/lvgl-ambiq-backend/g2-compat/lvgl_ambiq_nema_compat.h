/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_AMBIQ_NEMA_COMPAT_H
#define OPEN_CFW_LVGL_AMBIQ_NEMA_COMPAT_H

/*
 * AmbiqSuite 5.1.0's public nema_hal.c exports these two port helpers but its
 * public nema_hal.h omits their declarations. Keep the declarations in the
 * LVGL/Ambiq seam instead of modifying the authenticated Nema headers.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "nema_hal.h"

void nema_buffer_invalidate(nema_buffer_t * buffer);
bool nema_buffer_is_within_pool(int pool, uint32_t start, uint32_t length);

#endif /* OPEN_CFW_LVGL_AMBIQ_NEMA_COMPAT_H */
