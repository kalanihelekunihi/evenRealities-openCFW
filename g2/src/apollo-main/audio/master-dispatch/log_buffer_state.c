/* Observed Apollo logger storage; initial contents and startup are still open.
 * The EasyLogger singleton (RAM 0x20070be8) and line buffer log_buf
 * (RAM 0x2006bd30) are the statics `elog` and `log_buf` of the upstream
 * EasyLogger elog.c unit and are no longer defined here. */
#include <stdint.h>

/* Fix 38: compress_log ring {base, capacity, read, write}. Stock .data init at 0x200004c8 =
 * {0x200ccbd8, 0x8000, 0, 0} (.waves/init_20000000.bin +0x4c8; stock 0x43d040 reads
 * +4/+8/+12 of this cell). It was zero-initialised here, so audio_log_emit (stock 0x43ca50)
 * saw capacity 0 / free 0xffffffff and memcpy'd every packet to address 0. The 32 KiB
 * storage (stock RAM 0x200ccbd8..0x200d4bd8) is owned below. */
/* R2: external linkage so the stock .data shadow word in system/stock-ram can
 * relocate against it. */
uint8_t g2_compress_log_ring_storage_200ccbd8[0x8000u] __attribute__((aligned(4)));
volatile uint32_t g2_audio_log_ring_state[4]
    __attribute__((section(".g2_ram_200004c8"))) = {
    (uint32_t)(uintptr_t)g2_compress_log_ring_storage_200ccbd8, 0x8000u, 0u, 0u};
