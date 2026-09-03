/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_log_provider.h"

void open_cfw_lvgl_log_probe(lv_log_level_t level, const char * file, int line,
                             const char * function, const char * message)
{
    lv_log_add(level, file, line, function, "%s", message);
}
