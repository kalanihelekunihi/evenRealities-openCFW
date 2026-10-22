/* GX8002B voice codec host driver (stock driver/codec/drv_gx8002b.c,
 * native 0x57a46c..0x57a86f).
 *
 * The GX8002B is the I2S clock master; Apollo510 I2S0 runs as an RX-only
 * slave and double-buffers 3,200-byte DMA blocks. Power is three codec
 * control lines driven through the codec GPIO selector (0x509024). */
#ifndef G2_DRV_GX8002B_H
#define G2_DRV_GX8002B_H

#include <stdint.h>

#define G2_GX8002_I2S_BLOCK_BYTES 3200u

void gx8002_i2s_isr(void);
void DRV_Gx8002_PowerOn(void);
void DRV_Gx8002_PowerOff(void);
uint8_t gx8002_power_state_get(void);
void DRV_Gx8002_I2SInit(void);
void DRV_Gx8002_I2SDeinit(void);
/* Publishes the inactive RX DMA buffer (after D-cache invalidate) and its
 * fixed 3,200-byte length. The buffer is borrowed from the DMA ping/pong. */
void gx8002_i2s_rx_buffer_get(uint8_t **buffer, uint32_t *length);
void gx8002_audio_thread_notify(void);
/* Power-cycles the codec; skip_boot_wait == 0 waits a further 1.5 s. */
void DRV_Gx8002_Reboot(uint8_t skip_boot_wait);

#endif
