/* Persistent OTA bootloader flag page at Apollo mapped flash 0x007fe000.
 * The first word is read as a scalar by OTA_FileSystemSetBootloaderFlag;
 * the guarded NVM writer programs all four words. No default is assumed. */
#include <stdint.h>

volatile uint32_t audio_ble_bootloader_flag[4]
    __attribute__((section(".bss.opencfw.ota.bootloader_flag"), aligned(16), used));

_Static_assert(sizeof(audio_ble_bootloader_flag) == 16u, "OTA flag write extent");
