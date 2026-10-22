/* Touch-controller firmware update service (stock
 * platform\input\touchDFU\service_touch_dfu.c, native 0x55fcb4..0x56170f).
 *
 * The PSoC 4000T resident bootloader speaks the Infineon/Cypress DFU (cy_dfu)
 * host protocol over the same I2C transport as the touch driver:
 *   frame = 01 <cmd> <len u16 LE> <payload, len <= 32> <sum16 LE> 17
 *   sum16 = two's complement of the byte sum over SOP, cmd, len and payload.
 * Replies use the same framing with the cy_dfu status code in the command
 * byte (0 = success) and are read as 15 bytes, polled up to 100 times with
 * a 1 ms delay before each read. Host-side reply errors: 0xaa bad start or
 * short frame, 3 bad length, 4 missing end byte, 8 checksum mismatch.
 *
 * Commands: 0x38 enter (product ID 0x01020304), 0x4c set app metadata
 * (app 1, start 0x3300, length), 0x37 send data (<= 32 B), 0x49 program
 * row (address + 0x3300, CRC-32C of the 128-byte row), 0x31 verify app 1,
 * 0x3b exit (no reply). The image comes from /firmware/touch.bin (FWPK
 * container, record type 3); the record's last 4 bytes are not programmed. */
#ifndef G2_TOUCH_DFU_H
#define G2_TOUCH_DFU_H

#include <stdint.h>

int32_t TouchEnterDFU(void);
int32_t TouchSetAppMeta(uint32_t length);
int32_t TouchSendOnePacket(const void *data, uint16_t len);
int32_t TouchProgramData(uint32_t offset, uint32_t crc32c);
int32_t TouchVerifyApp(void);
int32_t TouchExitDFU(void);
int32_t TouchSendAppFile(const uint8_t *image, int32_t length);
void free_touch_firmware_memory(void);
int32_t get_touch_firmware_package_version(uint32_t *version);
int32_t load_touch_firmware_from_package(void);
uint32_t isTouchNeedUpgrade(uint32_t current, uint32_t package);
const char *semantic_TouchLogCurrentVersion(void);
void TouchUpdateFirmwareCheck(uint8_t force);

#endif
