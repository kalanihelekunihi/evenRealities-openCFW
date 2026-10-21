/* Native ROM pointer retained separately when Clang folds the SDK singleton. */
#include "nrf_atfifo.h"
extern nrf_atfifo_t r1_sdk_fstorage_sd_fifo_inst;
nrf_atfifo_t * const r1_sdk_fstorage_sd_fifo_pointer
 __attribute__((section(".r1.fstorage_sd.fifo_pointer"),used))=&r1_sdk_fstorage_sd_fifo_inst;
_Static_assert(sizeof(nrf_atfifo_t)==16,"native FIFO control extent");
