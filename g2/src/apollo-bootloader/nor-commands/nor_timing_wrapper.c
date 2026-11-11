/* SPDX-License-Identifier: MIT
 * Stock 0x4201ba: run the NOR MSPI timing scan into a cleared local record and
 * apply/log the result (opencfw_provider_4201ba_core in nor_commands.c).
 * The scan fills six bytes; the core copies eight, so the tail is zeroed too.
 */
#include <stdint.h>

#include "nor_commands.h"

extern void opencfw_provider_4201ba_core(uint8_t *scan_timing);

void opencfw_provider_4201ba(void)
{
    uint8_t scan_timing[8] __attribute__((aligned(8))) = {0};

    opencfw_provider_4201ba_core(scan_timing);
}
