/* Minimum native-observed productMode state at 0x200038f0.
 * Native 0x4abe66 writes byte 0; native 0x4abe60 reads byte 1.
 * The full generated object extent and startup values remain unknown. */
#include <stdint.h>

/* Fix 34: stock nvProdMode is 4 bytes: the FlashDB default KV table registers it with
 * length 4 (stock node 0x20003868 entry 2, key 0x78bfb4; storage_data.c:183), so a
 * 2-byte object let NVDB loads overwrite the next object (g2_uart_sync_module).
 * Stock .data init at 0x200038f0 is 01 00 00 00 (.waves/init_20000000.bin +0x38f0). */
volatile uint8_t g2_uart_product_mode_state[4] __attribute__((aligned(4)))
    __attribute__((section(".g2_ram_200038f0"))) = {1u, 0u, 0u, 0u};
