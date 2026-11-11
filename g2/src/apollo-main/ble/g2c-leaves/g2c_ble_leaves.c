/* g2c wave 2: small first-party BLE leaves decompiled from 2.2.6.10.
 * Profile g2-apollo-main-1. */
#include <stdint.h>

/* App DB / privacy record table, RAM 0x20067a30 (literal at 0x47ae64):
 * 10 records x 200 bytes; +0x2f = inUse, +0x30 = valid (wave20 upstream match:
 * cordio ble-profiles/sources/af/common/app_db.c appDbRec_t. arm-none-eabi-gcc offsetof
 * gives inUse 0x2f and valid 0x30 for every 200-byte CCCD/HDL_LIST config, and
 * AppDbRecordInUse's upstream body is the same loop. Stock strings name
 * third_party\cordio\...\app\common\app_db.c.)
 * +0xc3 is the link role byte (wave22 verified at stock 0x47a7f2, strb r5,[r6,#195] in
 * AppDbNewRecord 0x47a71c, ghidra/open-2026-09-29 decomp/0047a71c.c): it stores the role
 * argument, and the log "Database full for role: %s" (pool 0x47ae68) prints "Master" when it is
 * nonzero (pool 0x47a8a4) and "Slave" when 0 (0x47a8a8). The per-role count 0x47a676 compares it;
 * more than 4 records deletes the oldest. +0xc4 is a 32-bit age stamp from the counter at pool
 * 0x47ae50. This vendor field has no upstream counterpart (upstream discStatus is at 0xc4/0xc6). */
extern uint8_t audio_ble_privacy_rows[];
#define G2C_APPDB_RECORDS   10u
#define G2C_APPDB_REC_SIZE  200u

/* Stock 0x0047a5d0 (AppDbRecordInUse-like) */
uint32_t AppDbRecordInUse_47a5d0(const uint8_t *rec)
{
    const uint8_t *p = audio_ble_privacy_rows;
    for (uint32_t i = 0; i < G2C_APPDB_RECORDS; i++, p += G2C_APPDB_REC_SIZE) {
        if (p[0x2f] != 0u && p[0x30] != 0u && p == rec)
            return 1u;
    }
    return 0u;
}

/* Stock 0x0047a676: count in-use records whose byte +0xc3 equals kind. */
uint8_t app_db_paired_count_47a676(uint8_t kind)
{
    const uint8_t *p = audio_ble_privacy_rows;
    uint8_t n = 0u;
    for (uint8_t i = 0; i < G2C_APPDB_RECORDS; i++, p += G2C_APPDB_REC_SIZE) {
        if (p[0x2f] != 0u && p[0xc3] == kind)
            n++;
    }
    return n;
}
__typeof__(app_db_paired_count_47a676) audio_ble_pair_count
    __attribute__((alias("app_db_paired_count_47a676")));

/* Stock 0x00532e7c AppDiscRegister: stores the callback at RAM 0x20074348. */
extern uintptr_t audio_ble_service_dispatch_20074348;
void app_disc_register_532e7c(void (*cback)(uint8_t, uint8_t))
{
    audio_ble_service_dispatch_20074348 = (uintptr_t)cback;
}

/* Stock 0x004b4dc4: radio reset used by the AT CLI. */
extern uint32_t audio_ble_hci_error_check_4b47ae(uint32_t code);
extern void audio_ble_hci_driver_radio_shutdown(void);   /* 0x4b49ce */
extern void audio_ble_hci_driver_radio_boot(uint8_t);    /* 0x4b48a6 */
extern void audio_ble_hci_driver_empty_queue_4b4d18(void);
extern void DmDevReset(void);                            /* 0x4b3026 */
void ble_hci_radio_reset_4b4dc4(void)
{
    (void)audio_ble_hci_error_check_4b47ae(1u);
    audio_ble_hci_driver_radio_shutdown();
    audio_ble_hci_driver_radio_boot(0u);
    audio_ble_hci_driver_empty_queue_4b4d18();
    DmDevReset();
}
