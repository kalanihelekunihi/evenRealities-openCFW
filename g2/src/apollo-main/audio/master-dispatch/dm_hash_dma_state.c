/* Source-owned live RAM used by the selected DM hash and DMA queue paths. */
#include <stdint.h>

/* The native copy path writes sixteen bytes from the database hash pointer. */
uint8_t audio_ble_dm_database_hash_20068215[16];

/* The native queue path accepts channels 0..11 and indexes 0x2c-byte rows. */
uint8_t audio_ble_dma_channel_rows_2006ef28[12u * 0x2cu];
