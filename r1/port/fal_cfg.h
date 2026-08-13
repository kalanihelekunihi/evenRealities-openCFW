#ifndef OPENR1_FAL_CFG_H
#define OPENR1_FAL_CFG_H

#define FAL_PRINTF(...) ((void)0)
#define FAL_DEBUG 0
#define FAL_PART_HAS_TABLE_CFG

struct fal_flash_dev;
extern const struct fal_flash_dev r1_fal_flash_device;

#define FAL_FLASH_DEV_TABLE { &r1_fal_flash_device }
#define FAL_PART_TABLE { \
    {UINT32_C(0x45503130), "kv.bin",     "device_flash", 0x00000, 0x02000, 0}, \
    {UINT32_C(0x45503130), "health.db",  "device_flash", 0x02000, 0x06000, 0}, \
    {UINT32_C(0x45503130), "sleep.db",   "device_flash", 0x08000, 0x02000, 0}, \
    {UINT32_C(0x45503130), "pKey.bin",   "device_flash", 0x0a000, 0x01000, 0}, \
    {UINT32_C(0x45503130), "reserve",    "device_flash", 0x0b000, 0x0b000, 0}, \
    {UINT32_C(0x45503130), "ep.bin",     "device_flash", 0x16000, 0x02000, 0}, \
    {UINT32_C(0x45503130), "log.bin",    "device_flash", 0x18000, 0x0c000, 0}, \
}

#endif
