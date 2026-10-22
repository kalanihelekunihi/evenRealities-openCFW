/* Prioritised init-function table, stock ROM 0x6d1e0c..0x6d1ec3: 23
 * {fn, priority} records collected by the IAR linker (__section_begin/
 * __section_end) and run by auto_init_table_run_5bf0bc (x-03-init). Here the
 * collected table is one const array; its end bound is an assembler alias at
 * +0xb8 so the runner's (end - start) >> 3 count stays 23.
 *
 * Records decoded from the stock image (VA = file offset + 0x437fe0); each
 * function is resolved by address to its linked g2/src definition. Three
 * functions (0x47ee60, 0x5bf9f6, 0x50af86) have no g2/src definition or TSV
 * row yet and are referenced by provisional g2_init_entry_<addr> names. */
#include <stdint.h>

typedef struct {
    void (*fn)(void);   /* +0x0 */
    int32_t priority;   /* +0x4 */
} g2_init_entry_t;
_Static_assert(sizeof(g2_init_entry_t) == 8u, "init table record");

void audio_file_redirect_init_474d9c(void); /* 0x474d9c */
void audio_file_tlsf_pool_init_5eda64(void); /* 0x5eda64 */
void board_init_5093ac(void); /* 0x5093ac */
void board_init_5cdd14(void); /* 0x5cdd14 */
void board_power_init_5093d4(void); /* 0x5093d4 */
void g2_init_entry_47ee60(void); /* 0x47ee60 */
void g2_init_entry_50af86(void); /* 0x50af86 */
void g2_init_entry_5bf9f6(void); /* 0x5bf9f6 */
void kvdbAlsScaleDefaultInitialize(void); /* 0x4aeca4 */
void kvdbRingDefaultInitialize(void); /* 0x5d9b6c */
void kvdbSettingDefaultInitialize(void); /* 0x4aeb20 */
void kvdbTemperatureUnitDefaultInitialize(void); /* 0x49b014 */
void kvdbTerminalModeDefaultInitialize(void); /* 0x4b03e0 */
void kvdbTimeDefaultInitialize(void); /* 0x585618 */
void kvdbTimeFormatDefaultInitialize(void); /* 0x49ae90 */
void kvdbUniversalSettingDefaultInitialize(void); /* 0x49ad0c */
void nvdbAdvMagicDefaultCrcInitialize(void); /* 0x5d9ed0 */
void nvdbBuzzerDefaultCrcInitialize(void); /* 0x58f9d4 */
void nvdbMacDefaultInitialize(void); /* 0x5d9f48 */
void nvdbSensorCaldataAgDefaultInitialize(void); /* 0x509984 */
void nvdbSensorCaldataDefaultInitialize(void); /* 0x509764 */
void nvdbSysDtDefaultInitialize(void); /* 0x4aee28 */
void productModeDefaultCrcInitialize(void); /* 0x4abd90 */

/* ROM 0x6d1e0c */
const g2_init_entry_t g2_init_table_start_6d1e0c[23] __attribute__((aligned(4))) = {
    {board_power_init_5093d4, 100}, /* ROM 0x6d1e0c */
    {board_init_5093ac, 1}, /* ROM 0x6d1e14 */
    {g2_init_entry_47ee60, 1}, /* ROM 0x6d1e1c */
    {g2_init_entry_5bf9f6, 1}, /* ROM 0x6d1e24 */
    {board_init_5cdd14, 0}, /* ROM 0x6d1e2c */
    {audio_file_redirect_init_474d9c, 25}, /* ROM 0x6d1e34 */
    {kvdbAlsScaleDefaultInitialize, 75}, /* ROM 0x6d1e3c */
    {kvdbRingDefaultInitialize, 75}, /* ROM 0x6d1e44 */
    {kvdbSettingDefaultInitialize, 75}, /* ROM 0x6d1e4c */
    {kvdbTemperatureUnitDefaultInitialize, 75}, /* ROM 0x6d1e54 */
    {kvdbTerminalModeDefaultInitialize, 75}, /* ROM 0x6d1e5c */
    {kvdbTimeDefaultInitialize, 75}, /* ROM 0x6d1e64 */
    {kvdbTimeFormatDefaultInitialize, 75}, /* ROM 0x6d1e6c */
    {kvdbUniversalSettingDefaultInitialize, 75}, /* ROM 0x6d1e74 */
    {nvdbAdvMagicDefaultCrcInitialize, 75}, /* ROM 0x6d1e7c */
    {nvdbBuzzerDefaultCrcInitialize, 75}, /* ROM 0x6d1e84 */
    {nvdbMacDefaultInitialize, 75}, /* ROM 0x6d1e8c */
    {productModeDefaultCrcInitialize, 75}, /* ROM 0x6d1e94 */
    {nvdbSensorCaldataDefaultInitialize, 75}, /* ROM 0x6d1e9c */
    {nvdbSensorCaldataAgDefaultInitialize, 75}, /* ROM 0x6d1ea4 */
    {nvdbSysDtDefaultInitialize, 75}, /* ROM 0x6d1eac */
    {audio_file_tlsf_pool_init_5eda64, 26}, /* ROM 0x6d1eb4 */
    {g2_init_entry_50af86, 100}, /* ROM 0x6d1ebc */
};
_Static_assert(sizeof g2_init_table_start_6d1e0c == 0xb8u, "0x6d1e0c..0x6d1ec3");

/* ROM 0x6d1ec4: end bound of the collected table. */
__asm__(".globl g2_init_table_end_6d1ec4\n"
        ".set g2_init_table_end_6d1ec4, g2_init_table_start_6d1e0c + 0xb8\n"
        ".type g2_init_table_end_6d1ec4, %object\n"
        ".size g2_init_table_end_6d1ec4, 0\n");

/* RAM 0x20066a30: sorted working copy (at most 256 records, 0x800 B). */
g2_init_entry_t g2_init_table_sorted_20066a30[256];
