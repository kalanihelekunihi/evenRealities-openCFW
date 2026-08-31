/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_AMBIQ_NEMA_BUFFER_HELPERS_H
#define OPEN_CFW_LVGL_AMBIQ_NEMA_BUFFER_HELPERS_H

#include <stdbool.h>
#include <stdint.h>

#include "nema_hal.h"

#ifdef __cplusplus
extern "C" {
#endif

void nema_buffer_invalidate(nema_buffer_t *buffer);
bool nema_buffer_is_within_pool(int pool, uint32_t start, uint32_t length);

#ifdef __cplusplus
}
#endif

#endif
