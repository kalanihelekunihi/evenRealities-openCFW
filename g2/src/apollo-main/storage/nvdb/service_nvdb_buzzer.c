/* NVDB buzzer record, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\NV\service_nvdb_buzzer.c.
 * Native 0x58f9d4..0x58fa8f; literal pool 0x58fa90..0x58faab.
 *
 * Record "nvBuzzer" (12 bytes): version 2, u32 frequency at +4, u8 duty at +8,
 * CRC16 over 10 bytes at +10. Live copy RAM 0x200038d8. */
#include <stdint.h>
#include "nvdb_internal.h"

extern g2_nvdb_buzzer_t g2_nvdb_buzzer_record; /* RAM 0x200038d8 */

static const char module_tag[] = "nv.buzzer"; /* ROM 0x78bff0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\NV\\service_nvdb_buzzer.c"; /* ROM 0x6e4f88 */
static const char key_buzzer[] = "nvBuzzer"; /* ROM 0x78bffc */
static const char update_fn[] = "_nvdbUpdataBuzzer"; /* ROM 0x78344c */
static const char debug_only[] = "!!This is only for program debugging"; /* ROM 0x74e04c */
static const char debug_only_short[] = "[nv.buzzer]!!This is only for program debugging"; /* ROM 0x738594 */

int32_t nvdbBuzzerDefaultCrcInitialize(void)
{
    g2_nvdb_buzzer_record.crc = audio_uart_hand_checksum_49acd4(&g2_nvdb_buzzer_record, 10u, NULL);
    return 0;
}

int32_t _nvdbUpdataBuzzer(void)
{
    g2_nvdb_buzzer_t stored;
    NVDB_LOG(module_tag, source_file, 2u, update_fn, 0x2eu, 0x08000000u, debug_only, debug_only_short);
    if (SVC_NvdbRead(key_buzzer, &stored, 12u) < 1)
        nvdbBuzzerUpdate(g2_nvdb_buzzer_record.frequency, g2_nvdb_buzzer_record.duty);
    else if (stored.crc != g2_nvdb_buzzer_record.crc && stored.version < 2u)
        nvdbBuzzerUpdate(g2_nvdb_buzzer_record.frequency, g2_nvdb_buzzer_record.duty);
    return 0;
}

uint32_t nvdbBuzzerFrequencyGet(void)
{
    return g2_nvdb_buzzer_record.frequency;
}

uint8_t nvdbBuzzerDutyGet(void)
{
    return g2_nvdb_buzzer_record.duty;
}

void nvdbBuzzerUpdate(uint32_t frequency, uint8_t duty)
{
    g2_nvdb_buzzer_t *rec = &g2_nvdb_buzzer_record;
    rec->frequency = frequency;
    rec->duty = duty;
    rec->version = 2u;
    rec->crc = audio_uart_hand_checksum_49acd4(rec, 10u, NULL);
    (void)SVC_NvdbWrite(key_buzzer, rec, 12u);
}
