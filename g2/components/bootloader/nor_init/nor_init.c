/* SPDX-License-Identifier: MIT
 * Readable source candidates for locked bootloader functions 0x420476 and
 * 0x42059e. MSPI/HAL, command, logging, delay, and runtime side effects remain
 * exact-address providers; their hardware behavior is outside this component.
 */
#include "nor_init.h"
#include "nor_read_status.h"
#include <stddef.h>

#include "../nor_mspi_init/nor_mspi_init.h"
extern void opencfw_provider_41f9d8(uint32_t amount);
extern void opencfw_provider_42052a(void);
extern void opencfw_provider_420f10(void);
extern void opencfw_provider_4201ba(void);
extern void opencfw_provider_420890(void);
extern void opencfw_provider_420c5c(uint32_t mode);
extern void opencfw_provider_41fe62(void);
extern void opencfw_provider_41fe28(void);
extern void opencfw_provider_4176ce(uint32_t level, const char *module,
                                    const char *file, const char *function,
                                    uint32_t line, const char *format, ...);

static const char nor_module[] = "drv.norflash";
static const char nor_source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c";
static const char nor_init_function[] = "DRV_Mx25u25643g_init";
static const char nor_read_id_function[] = "DRV_Mx25u25643g_read_id";
static const char flash_init_failed[] = "Flash init fail: %d\n";
static const char flash_id_failed[] = "command_read ERROR\n";
static const char flash_init_id_failed[] = "Flash ID fail: %d\n";
static const char flash_id_report[] = "Flash ID: 0x%06X\n";

uint32_t opencfw_bl_nor_read_jedec_id(uint32_t *out_id,
                                      uint32_t reserved1,
                                      uint32_t reserved2,
                                      uint32_t initial_word)
{
    (void)reserved1;
    (void)reserved2;
    uint32_t raw = initial_word;
    const uint32_t status = opencfw_bl_mspi_status_transfer(
        0x9fu, 0u, 0u, &raw, 3u);
    if (status == 0u) {
        const uint8_t *bytes = (const uint8_t *)&raw;
        *out_id = ((uint32_t)bytes[0] << 16) |
                  ((uint32_t)bytes[1] << 8) |
                  (uint32_t)bytes[2];
    } else {
        opencfw_provider_4176ce(1u, nor_module, nor_source_file,
            nor_read_id_function, 0x2d8u, flash_id_failed);
    }
    return status;
}

uint32_t opencfw_provider_420476(void)
{
    uint32_t result = opencfw_provider_420254(1u, NULL,
        (void **)(uintptr_t)0x200270d8u, 0u);
    if (result != 0u) {
        opencfw_provider_4176ce(1u, nor_module, nor_source_file,
            nor_init_function, 0x284u, flash_init_failed, result);
    } else {
        opencfw_provider_41f9d8(10u);
        opencfw_provider_42052a();
        opencfw_provider_420f10();
        opencfw_provider_4201ba();
        opencfw_provider_420f10();

        uint32_t jedec_id = 0u;
        result = opencfw_bl_nor_read_jedec_id(&jedec_id, 0u, 0u, 0u);
        if (result != 0u) {
            opencfw_provider_4176ce(1u, nor_module, nor_source_file,
            nor_init_function, 0x28eu, flash_init_id_failed, result);
        } else {
            opencfw_provider_4176ce(3u, nor_module, nor_source_file,
                nor_init_function, 0x292u, flash_id_report, jedec_id);
            opencfw_provider_420890();
            opencfw_provider_420c5c(1u);
            opencfw_provider_41fe62();
        }
    }
    opencfw_provider_41fe28();
    return result;
}
