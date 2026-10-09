/* Include unchanged, sealed selected SDK text to expose its private blocking body.
 * Only the type0 path used by codec_channel_tx is reconstructed here. */
#include "../uart_tx_offline/am_hal_uart.c"
uint32_t codec_hal_blocking(void *handle,const void *transfer){
 if(!AM_HAL_UART_CHK_HANDLE(handle))return 2;
 return blocking_write(handle,(const am_hal_uart_transfer_t *)transfer);
}
