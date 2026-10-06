/* SPDX-License-Identifier: MIT
 * Reconstructed Apollo510 bootloader MSPI power-control private ABI.
 */
#ifndef OPENCFW_BOOT_NOR_MSPI_POWER_CONTROL_H
#define OPENCFW_BOOT_NOR_MSPI_POWER_CONTROL_H

#include <stdint.h>

typedef struct {
    uint32_t (*mode_enter)(uint8_t user_id); /* stock 0x41bf84 */
    uint32_t (*mode_leave)(uint8_t user_id); /* stock 0x41c17a */
    uint32_t (*clock_request)(uint8_t clock_id, uint8_t user_id);
    uint32_t (*clock_release_all)(uint8_t user_id);
    void (*clockgen)(uint32_t module, uint8_t enable, uint8_t configure,
                     uint8_t source);
    uint32_t (*cq_disable)(uint32_t *handle);
    void (*cq_enable)(uint32_t *handle);
    uint32_t (*interrupt_disable)(uint32_t *handle, uint32_t mask);
    void (*delay_us)(uint32_t duration);
    uint32_t (*mmio_read)(uint32_t module, uint16_t offset);
    void (*mmio_write)(uint32_t module, uint16_t offset, uint32_t value);
} opencfw_mspi_power_ops_t;

/* operation 0 follows the stock operation-0 branch; operations 1 and 2 both
 * power down. retain_state is byte-valued, as in the original third argument.
 */
uint32_t opencfw_hal_mspi_power_control(uint32_t *handle,
                                        uint32_t operation,
                                        uint32_t retain_state,
                                        const opencfw_mspi_power_ops_t *ops);

#endif
