/* OTA MRAM flash backend, stock Apollo main 0x5a4ef4..0x5a4fa0
 * (literal pool word 0x5a4fa0 = RAM 0x200742ec), firmware 2.2.6.10.
 *
 * The three entry points are the read/program/erase slots of the MRAM
 * backend vtable at RAM 0x2000038c (app/S3-app-data/ota_efs_data.c:
 * {.., 0x5a4f31, 0x5a4f59, 0x5a4f81}). Each one validates the request with
 * the range check at 0x5a4ef4; that check is its only callee set
 * (callers 0x5a4f3c, 0x5a4f64, 0x5a4f88).
 *
 * Reconstructed from the stock disassembly; compilation is not byte identity. */
#include <stdint.h>

/* am_hal_mcuctrl_info_get(AM_HAL_MCUCTRL_INFO_DEVICEID = 1, &device), stock
 * 0x480d72. The existing hand definition carries this name; the 64-byte
 * am_hal_mcuctrl_device_t record (AmbiqSuite 5.1.0) has ui32MRAMSize at +0x2c. */
extern uint32_t audio_ble_hci_radio_identifier_480d72(uint8_t mode, void *output);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);   /* memcpy 0x439be4 */
extern void mram_program_bytes_47cbe8(uint8_t *destination, const uint8_t *source,
                                      uint32_t length);                           /* 0x47cbe8 */

/* RAM 0x200742ec (.bss, outside the 0x20000000..0x20004558 init image):
 * MRAM size cached from the device-info record on first use. */
static uint32_t ota_mram_size_200742ec;

/* Stock 0x5a4ef4..0x5a4f30. Returns 1 when the request may proceed: the address
 * is at or above the 16 KiB boot region and the length is below the MRAM size.
 * Stock also computes address + length - 1 and discards it; the end address is
 * not checked. */
uint32_t ota_mram_range_check_5a4ef4(uint32_t address, uint32_t length)
{
    if (ota_mram_size_200742ec == 0u) {
        uint32_t device[16];
        (void)audio_ble_hci_radio_identifier_480d72(1u, device);
        ota_mram_size_200742ec = device[11]; /* ui32MRAMSize */
    }
    if (address < 0x4000u)
        return 0u;
    if (length >= ota_mram_size_200742ec)
        return 0u;
    return 1u;
}

/* Stock 0x5a4f30..0x5a4f58: MRAM is memory mapped, so a read is a copy. */
int32_t ota_mram_read_5a4f30(void *dst, uint32_t address, uint32_t length)
{
    if (ota_mram_range_check_5a4ef4(address, length) == 0u)
        return -1;
    (void)audio_queue_copy_bytes(dst, (const void *)(uintptr_t)address, length);
    return 0;
}

/* Stock 0x5a4f58..0x5a4f80. */
int32_t ota_mram_program_5a4f58(uint32_t address, const void *src, uint32_t length)
{
    if (ota_mram_range_check_5a4ef4(address, length) == 0u)
        return -1;
    mram_program_bytes_47cbe8((uint8_t *)(uintptr_t)address, (const uint8_t *)src, length);
    return 0;
}

/* Stock 0x5a4f80..0x5a4fa0. MRAM needs no erase: after the range check
 * (length 4) the stock body moves the address to r0 and runs two NOPs (a
 * removed call) before returning 0. */
int32_t ota_mram_erase_5a4f80(uint32_t address)
{
    if (ota_mram_range_check_5a4ef4(address, 4u) == 0u)
        return -1;
    return 0;
}
