/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_AMBIQ_LOG_PROVIDER_H
#define OPEN_CFW_LVGL_AMBIQ_LOG_PROVIDER_H

#include "src/misc/lv_log.h"

#ifdef __cplusplus
extern "C" {
#endif

void lv_log_add(lv_log_level_t level, const char * file, int line,
                const char * function, const char * format, ...);

#ifdef __cplusplus
}
#endif

#endif
