/* Native 0x47cbc4..0x47cbe8 (CRC-32C update) and 0x47cbe8..0x47cc14
 * (MRAM byte-range program). No source path string survives for this unit.
 *
 * 0x47cbc4 is the EVENOTA / EFS file checksum: CRC-32C polynomial 0x1EDC6F41,
 * non-reflected (MSB-first), table at ROM 0x6983a8, caller-held running value
 * (init 0, no xorout; see g2/docs/reference/firmware-formats.md). Callers:
 * _fileRawDataParse 0x446d40, _fileCaculateCRC 0x447a60/0x4567b8,
 * _efsFileRawDataParse 0x457a54, _parseWhiteListFromFS 0x4d6360.
 *
 * 0x47cbe8 programs MRAM with interrupts masked; its only caller is the AT
 * memory-write helper 0x5a4f58 after a range check. */
#include <stdint.h>

extern const uint32_t g2_crc32c_msb_table[256]; /* ROM 0x6983a8, entry[1] = 0x1edc6f41 */

extern uint32_t g2_gpio_critical_save(void); /* 0x473940: MRS PRIMASK; CPSID i */
/* 0x4d0a2c: am_hal_mram_main_program-style (key, source words, destination, word count). */
extern uint32_t audio_ble_nvm_write_words(uint32_t, const uint8_t *, uint8_t *, uint32_t);

#define G2_MRAM_PROGRAM_KEY 0x12344321u /* pool 0x47cc18 */

void file_crc32c_update_47cbc4(const uint8_t *data, uint32_t length, uint32_t *crc)
{
    uint32_t value = *crc;
    for (uint32_t i = 0u; i < length; i++)
        value = g2_crc32c_msb_table[data[i] ^ (value >> 24)] ^ (value << 8);
    *crc = value;
}

/* Length is in bytes and rounded up to whole words; the program status is
 * discarded (stock returns whatever is in the r3 stack slot). */
void mram_program_bytes_47cbe8(uint8_t *destination, const uint8_t *source, uint32_t length)
{
    uint32_t saved;
    /* Stock carries two NOPs here (0x47cbf2/0x47cbf4). */
    __asm__ volatile("nop\n\tnop");
    saved = g2_gpio_critical_save();
    (void)audio_ble_nvm_write_words(G2_MRAM_PROGRAM_KEY, source, destination,
                                    (length + 3u) >> 2);
    __asm__ volatile("msr PRIMASK, %0" :: "r"(saved) : "memory");
}
