/* Digital microphone (Apollo510 PDM0) drivers.
 *
 * Two stock source files drive the same PDM0 block with the same
 * configuration but separate handles, DMA buffers and block sizes:
 *   driver/pdm/drv_pdm.c            native 0x57b704..0x57ba1d, 160-sample blocks
 *   driver/pdm/drv_pdm_production.c native 0x57b444..0x57b6a5, 1,600-sample blocks
 * PDM0_IRQHandler (in drv_pdm.c) services the production handle when
 * productModeGet() == 1 and the production bypass byte is clear. */
#ifndef G2_DRV_PDM_H
#define G2_DRV_PDM_H

#include <stdint.h>

#define G2_PDM_BLOCK_SAMPLES 160u
#define G2_PDM_PRODUCTION_BLOCK_SAMPLES 1600u

void DRV_PdmInit(void);
void DRV_PdmDeinit(void);
void PDM0_IRQHandler(void);
/* Converts the inactive DMA block to 16-bit PCM in a driver-owned scratch
 * buffer and publishes it with its byte length (320 / 3,200). */
void drv_pdm_buffer_get(uint8_t **buffer, uint32_t *length);

void DRV_PdmProductionInit(void);
void DRV_PdmProductionDeinit(void);
void drv_pdm_production_buffer_get(uint8_t **buffer, uint32_t *length);

#endif
