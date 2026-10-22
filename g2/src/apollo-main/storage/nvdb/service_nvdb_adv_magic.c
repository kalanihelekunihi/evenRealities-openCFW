/* NVDB advertising-magic record (no retained log strings; object adjacent to
 * service_nvdb_mac.c). Native 0x5d9ed0..0x5d9f3d; literal pool 0x5d9f40..0x5d9f47.
 *
 * Record "nvAdvMagic" (4 bytes): version 1, magic byte, CRC16 over 2 bytes.
 * Live copy RAM 0x200038d4. */
#include <stdint.h>
#include "nvdb_internal.h"

extern g2_nvdb_adv_magic_t g2_nvdb_adv_magic_record; /* RAM 0x200038d4 */

static const char key_adv_magic[] = "nvAdvMagic"; /* ROM 0x78bfe4 */

int32_t nvdbAdvMagicDefaultCrcInitialize(void)
{
    g2_nvdb_adv_magic_record.crc = audio_uart_hand_checksum_49acd4(&g2_nvdb_adv_magic_record, 2u, NULL);
    return 0;
}

int32_t nvdbAdvMagicLoadAndMigrate(void)
{
    g2_nvdb_adv_magic_t stored;
    if (SVC_NvdbRead(key_adv_magic, &stored, 4u) < 1)
        nvdbAdvMagicUpdate(g2_nvdb_adv_magic_record.magic);
    else if (stored.crc != g2_nvdb_adv_magic_record.crc && stored.version == 0u)
        nvdbAdvMagicUpdate(g2_nvdb_adv_magic_record.magic);
    return 0;
}

void nvdbAdvMagicUpdate(uint8_t magic)
{
    g2_nvdb_adv_magic_t *rec = &g2_nvdb_adv_magic_record;
    rec->magic = magic;
    rec->version = 1u;
    rec->crc = audio_uart_hand_checksum_49acd4(rec, 2u, NULL);
    (void)SVC_NvdbWrite(key_adv_magic, rec, 4u);
}
