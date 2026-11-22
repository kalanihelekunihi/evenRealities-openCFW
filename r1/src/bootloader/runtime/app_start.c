/* R1 bootloader handoff for the recovered flash map.
 * The stock S140 path starts at the first address after the MBR. The
 * source-built BLE path puts controller code there and has its application
 * vector at 0x27000 instead. This unit owns that choice in both profiles. */
#include <stdint.h>
#include "nrf.h"
#include "nrf_bootloader_app_start.h"
#include "nrf_dfu_mbr.h"
#include "nrf_log.h"
#include "nrf_log_ctrl.h"
#include "nrf_mbr.h"

extern void nrf_bootloader_app_start_final(uint32_t start_addr);

#define R1_APPLICATION_VECTOR_ADDRESS 0x27000u

void nrf_bootloader_app_start(void)
{
    uint32_t start_addr = MBR_SIZE;
#if defined(SVCALL_AS_NORMAL_FUNCTION)
    /* No S140 vector is present in the source-built BLE image. */
    start_addr = R1_APPLICATION_VECTOR_ADDRESS;
#endif

    /* The handoff helper only clears external IRQs. */
    NVIC->ICER[0] = 0xffffffffu;
    NVIC->ICPR[0] = 0xffffffffu;
#if defined(__NRF_NVIC_ISER_COUNT) && __NRF_NVIC_ISER_COUNT == 2
    NVIC->ICER[1] = 0xffffffffu;
    NVIC->ICPR[1] = 0xffffffffu;
#endif

#if defined(SVCALL_AS_NORMAL_FUNCTION)
    /* The source-built image has no S140/MBR interrupt relay. Select the
     * application table directly, as the application vector bridge does. */
    SCB->VTOR = R1_APPLICATION_VECTOR_ADDRESS;
    __DSB();
    __ISB();
#else
    uint32_t err_code = nrf_dfu_mbr_irq_forward_address_set();
    if (err_code != NRF_SUCCESS) {
        NRF_LOG_ERROR("MBR IRQ forwarding failed: 0x%x", err_code);
    }
#endif
    NRF_LOG_FLUSH();
    nrf_bootloader_app_start_final(start_addr);
}
