/* Print every SMP database record, stock
 * D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-profiles\sources\apps\app\common\app_db.c
 * (module "ble.smpdb"; G2-modified AmbiqSuite app_db.c, this function has no
 * upstream counterpart). Stock range 0x47ca9c..0x47cabd (literal pool entry
 * 0x47cbc0).
 *
 * Walks the ten 200-byte appDb records through the record-table pointer held
 * in ROM 0x78ee60 (value 0x20067a30) and logs each one with PrintSmpDbRecord
 * 0x4789b0 (ble/ble-privacy/display_ble_privacy_dump.c). */
#include <stdint.h>

#define APP_DB_NUM_RECS 10u
#define APP_DB_REC_SIZE 200u

extern uint8_t *const g2_appdb_rec_table_ptr_78ee60;       /* ROM 0x78ee60 = RAM 0x20067a30 */
extern void audio_ble_privacy_dump_row(uint8_t *record, uint8_t index); /* 0x4789b0 PrintSmpDbRecord */

/* Stock 0x0047CA9C (ble_appdb_print_all_47ca9c) */
void ble_appdb_print_all_47ca9c(void)
{
    uint8_t *record = g2_appdb_rec_table_ptr_78ee60;
    uint8_t i;

    for (i = 0u; i < APP_DB_NUM_RECS; i++) {
        audio_ble_privacy_dump_row(record, i);
        record += APP_DB_REC_SIZE;
    }
}
