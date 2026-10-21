/* SPDX-License-Identifier: MIT
 * Stock f89a4c46 literal pool at 0x42137c..0x4213c4 supplies this metadata.
 * Preserve EasyLogger's six fixed parameters before the format arguments.
 */
#ifndef OPENCFW_BOOT_MOUNT_LOG_H
#define OPENCFW_BOOT_MOUNT_LOG_H
#include <stdint.h>

extern void opencfw_boot_elog_output(uint32_t level, const char *tag,
    const char *file, const char *function, long line, const char *format, ...);

#define BOOT_MOUNT_LOG(level, function, line, format, ...) \
    opencfw_boot_elog_output((level), "file_system", \
        "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\port\\littlefs_mx25u25643g_porting.c", \
        (function), (line), (format), ##__VA_ARGS__)
#endif
