/* Native AppDbDeleteAllRecords 0x47acf8 and _evenEraseAllBondInfo 0x4787a4.
 * The ten 200-byte RAM rows and MRAM word count have separate live owners. */
#include <stdint.h>

extern uint8_t audio_ble_privacy_rows[10u * 200u]; /* 0x20067a30 */
extern uint8_t audio_ble_flash_staging_200636a0[]; /* live staging RAM */
extern volatile uint16_t audio_ble_bond_flash_bytes_20004524; /* live config */
extern uint8_t audio_ble_privacy_nvm_records[10u * 256u]; /* mapped MRAM 0x7ff000 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* selected 0x43c0e4 */
extern void audio_ble_privacy_cache_maintenance(const void *, uint8_t); /* selected 0x475014 */
extern uint32_t g2_gpio_critical_save(void); /* selected 0x473940 */
extern uint32_t audio_ble_nvm_write_words(uint32_t, const uint8_t *, uint8_t *, uint32_t); /* selected 0x4d0a2c */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "ble.smpdb";
static const char source[] = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char erase_function[] = "_evenEraseAllBondInfo";
static const char erase_fail[] = "Flash program failed: return code = 0x%x";
static const char erase_success[] = "Flash program success: return code = 0x%x";
static const char erase_fail_short[] = "[ble.smpdb]Flash program failed: return code = 0x%x";
static const char erase_success_short[] = "[ble.smpdb]Flash program success: return code = 0x%x";
static const char delete_function[] = "AppDbDeleteAllRecords";
static const char delete_message[] = "AppDbDeleteAllRecords";
static const char delete_short[] = "[ble.smpdb]AppDbDeleteAllRecords";

/* Stock 0x4787A4 (_evenEraseAllBondInfo; TSV FUN_004787a4) */
uint64_t audio_ble_privacy_erase_storage_body(uint32_t entry0, uint32_t entry1,
                                               uint32_t entry2, uint32_t entry3)
{
    (void)entry2; (void)entry3;
    audio_ble_privacy_cache_maintenance(0, 1u);
    uint32_t size = audio_ble_bond_flash_bytes_20004524;
    audio_uart_buffer_zero(audio_ble_flash_staging_200636a0, size, 0u);
    uint32_t saved = g2_gpio_critical_save();
    uint32_t result = audio_ble_nvm_write_words(0x12344321u,
                                                  audio_ble_flash_staging_200636a0,
                                                  audio_ble_privacy_nvm_records,
                                                  (uint16_t)(audio_ble_bond_flash_bytes_20004524 >> 2u));
    __asm__ volatile("msr PRIMASK, %0" :: "r"(saved) : "memory");
    if (result != 0u) {
        if (audio_log_level() & 2u) {
            entry0 = 0x8eu;
            entry1 = (uint32_t)(uintptr_t)erase_fail;
            audio_log_extended(1u, module, source, erase_function, 0x8eu, erase_fail, result);
        }
        if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
            (void)compressed_log_output(0x04400000u, erase_fail_short, erase_fail_short, result);
    } else {
        if (audio_log_level() & 2u) {
            entry0 = 0x90u;
            entry1 = (uint32_t)(uintptr_t)erase_success;
            audio_log_extended(4u, module, source, erase_function, 0x90u, erase_success, 0u);
        }
        if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
            (void)compressed_log_output(0x10400000u, erase_success_short, erase_success_short, 0u);
    }
    return ((uint64_t)entry1 << 32u) | entry0;
}

__attribute__((naked)) uint64_t audio_ble_privacy_erase_storage(void)
{
    __asm__ volatile("b audio_ble_privacy_erase_storage_body");
}

uint64_t audio_ble_privacy_reset_local_body(uint32_t entry0, uint32_t entry1,
                                             uint32_t entry2, uint32_t entry3)
{
    (void)entry0; (void)entry1;
    if (audio_log_level() & 2u) {
        entry2 = 0x45au;
        entry3 = (uint32_t)(uintptr_t)delete_message;
        audio_log_extended(4u, module, source, delete_function, 0x45au, delete_message);
    }
    if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
        (void)compressed_log_output(0x10000000u, delete_short, delete_short);
    for (uint32_t i = 0; i < 10u; ++i) {
        uint8_t *row = audio_ble_privacy_rows + i * 200u;
        row[0x2fu] = 0u;
        row[0x30u] = 0u;
        audio_uart_buffer_zero(row, 6u, 0u);
    }
    (void)audio_ble_privacy_erase_storage();
    return ((uint64_t)entry3 << 32u) | entry2;
}

/* Stock 0x47ACF8 (FUN_0047acf8, AppDbDeleteAllRecords) */
__attribute__((naked)) uint64_t audio_ble_privacy_reset_local(void)
{
    __asm__ volatile("b audio_ble_privacy_reset_local_body");
}
