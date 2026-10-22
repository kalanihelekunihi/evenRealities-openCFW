/* G2 factory NV database ("NVdb") records and public service API.
 *
 * Stock objects under D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\NV\:
 * service_nvdb.c (0x5105f0..0x510992), service_nvdb_sys_dt.c (0x4aee28..0x4b030a),
 * service_nvdb_product_mode.c (0x4abd90..0x4abe9e), service_nvdb_sensor_caldata.c
 * (0x509764..0x509aea), service_nvdb_buzzer.c (0x58f9d4..0x58fa90),
 * service_nvdb_mac.c / adv magic (0x5d9ed0..0x5da060).
 *
 * FlashDB database index 1 is the KVDB "factory" on FAL partition "NVdb"
 * (external NOR offset 0x01ff8000, 0x8000 bytes). Every record is a blob whose
 * first byte is a schema version and whose CRC16 (0x49acd4, seed 0xffff)
 * covers the bytes before the CRC field. The RAM image of each record is also
 * the value pointer of its FlashDB default node (table RAM 0x20003868). */
#ifndef G2_NVDB_H
#define G2_NVDB_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* "nvProdMode", RAM 0x200038f0, 4 bytes, version 1. */
typedef struct {
    uint8_t version;  /* +0x0 */
    uint8_t mode;     /* +0x1 productModeGet (0x4abe60) */
    uint16_t crc;     /* +0x2 CRC16 over bytes 0..1 */
} g2_nvdb_product_mode_t;
_Static_assert(sizeof(g2_nvdb_product_mode_t) == 4, "nvProdMode blob is 4 bytes");

/* "nvAdvMagic", RAM 0x200038d4, 4 bytes, version 1. */
typedef struct {
    uint8_t version;  /* +0x0 */
    uint8_t magic;    /* +0x1 */
    uint16_t crc;     /* +0x2 CRC16 over bytes 0..1 */
} g2_nvdb_adv_magic_t;
_Static_assert(sizeof(g2_nvdb_adv_magic_t) == 4, "nvAdvMagic blob is 4 bytes");

/* "nvBuzzer", RAM 0x200038d8, 12 bytes, version 2. */
typedef struct {
    uint8_t version;    /* +0x0 */
    uint8_t pad1[3];
    uint32_t frequency; /* +0x4 */
    uint8_t duty;       /* +0x8 */
    uint8_t pad9;
    uint16_t crc;       /* +0xa CRC16 over bytes 0..9 */
} g2_nvdb_buzzer_t;
_Static_assert(sizeof(g2_nvdb_buzzer_t) == 12, "nvBuzzer blob is 12 bytes");

/* "nvMAC", RAM 0x200038e4, 10 bytes, version 1. */
typedef struct {
    uint8_t version;  /* +0x0 */
    uint8_t mac[6];   /* +0x1 BD address, little-endian; mac[5] top bits 11 */
    uint8_t pad7;
    uint16_t crc;     /* +0x8 CRC16 over bytes 0..7 */
} g2_nvdb_mac_t;
_Static_assert(sizeof(g2_nvdb_mac_t) == 10, "nvMAC blob is 10 bytes");

/* "nvSCald", RAM 0x200038f4, 92 bytes, version 1. */
typedef struct {
    uint8_t version;      /* +0x00 */
    uint8_t pad1[3];
    float vec0[3];        /* +0x04 */
    float vec1[3];        /* +0x10 */
    float quat0[4];       /* +0x1c */
    float quat1[4];       /* +0x2c */
    float scalar;         /* +0x3c */
    float vec6[6];        /* +0x40 */
    uint16_t crc;         /* +0x58 CRC16 over bytes 0..0x57 */
    uint16_t pad5a;
} g2_nvdb_sensor_caldata_t;
_Static_assert(sizeof(g2_nvdb_sensor_caldata_t) == 0x5c, "nvSCald blob is 92 bytes");

/* "nvSCaldAG", RAM 0x20003950, 68 bytes, version 1. */
typedef struct {
    uint8_t version;      /* +0x00 */
    uint8_t pad1[3];
    float accel[3];       /* +0x04 accelerometer bias */
    float gyro[3];        /* +0x10 gyroscope bias */
    float matrix[9];      /* +0x1c 3x3 mounting matrix */
    uint16_t crc;         /* +0x40 CRC16 over bytes 0..0x3f */
    uint16_t pad42;
} g2_nvdb_sensor_caldata_ag_t;
_Static_assert(sizeof(g2_nvdb_sensor_caldata_ag_t) == 0x44, "nvSCaldAG blob is 68 bytes");

/* Aging timestamp copied as a 40-byte block; words 3..8 are logged as
 * year-month-day hour:minute:second. */
typedef struct {
    uint32_t word[10];
} g2_nvdb_aging_time_t;
_Static_assert(sizeof(g2_nvdb_aging_time_t) == 0x28, "aging time block is 40 bytes");

/* "nvSysDt", RAM 0x20003994, 172 bytes, version 2. The CRC covers only the
 * version and the two serial numbers (bytes 0..0x25). */
typedef struct {
    uint8_t version;                    /* +0x00 */
    char psn[15];                       /* +0x01 product SN, 14 chars + NUL (dataIdx 0) */
    char bsn[22];                       /* +0x10 board SN, 21 chars + NUL (dataIdx 1) */
    uint16_t crc;                       /* +0x26 */
    uint32_t lux_base;                  /* +0x28 (dataIdx 2) */
    uint8_t canvas_x;                   /* +0x2c (dataIdx 3) */
    uint8_t canvas_y;                   /* +0x2d (dataIdx 4) */
    uint8_t panel_current;              /* +0x2e (dataIdx 5) */
    uint8_t pad2f;
    g2_nvdb_aging_time_t aging_start;   /* +0x30 (dataIdx 6) */
    g2_nvdb_aging_time_t aging_end;     /* +0x58 (dataIdx 7) */
    g2_nvdb_aging_time_t aging_soc_to_10; /* +0x80 (dataIdx 8) */
    uint8_t aging_wrong_touch_times;    /* +0xa8 (dataIdx 9) */
    uint8_t aging_begin_charge_soc;     /* +0xa9 (dataIdx 10) */
    uint8_t aging_total_times;          /* +0xaa (dataIdx 11) */
    uint8_t aging_finish_flag;          /* +0xab (dataIdx 12) */
} g2_nvdb_sys_dt_t;
_Static_assert(sizeof(g2_nvdb_sys_dt_t) == 0xac, "nvSysDt blob is 172 bytes");
_Static_assert(offsetof(g2_nvdb_sys_dt_t, lux_base) == 0x28, "nvSysDt lux_base offset");
_Static_assert(offsetof(g2_nvdb_sys_dt_t, aging_soc_to_10) == 0x80, "nvSysDt aging offset");

/* SVC_NvdbWriteSysData dataIdx values (13 = whole 172-byte record). */
enum {
    G2_NVDB_SYSDT_PSN = 0,
    G2_NVDB_SYSDT_BSN = 1,
    G2_NVDB_SYSDT_LUX = 2,
    G2_NVDB_SYSDT_CANVAS_X = 3,
    G2_NVDB_SYSDT_CANVAS_Y = 4,
    G2_NVDB_SYSDT_PANEL_CURRENT = 5,
    G2_NVDB_SYSDT_AGING_START = 6,
    G2_NVDB_SYSDT_AGING_END = 7,
    G2_NVDB_SYSDT_AGING_SOC_TO_10 = 8,
    G2_NVDB_SYSDT_AGING_WRONG_TOUCH = 9,
    G2_NVDB_SYSDT_AGING_BEGIN_SOC = 10,
    G2_NVDB_SYSDT_AGING_TOTAL = 11,
    G2_NVDB_SYSDT_AGING_FINISH = 12,
    G2_NVDB_SYSDT_RECORD = 13,
};

/* service_nvdb.c */
int32_t SVC_NvdbRead(const char *key, void *buffer, uint16_t length);
int32_t SVC_NvdbWrite(const char *key, const void *buffer, uint16_t length);
uint8_t SVC_NvdbInit(void (*lock)(void *), void (*unlock)(void *));

/* service_nvdb_sys_dt.c */
int32_t SVC_NvdbWriteSysData(uint8_t data_index, const void *value);
uint8_t *SVC_NvdbReadSysData(uint8_t data_index);
void SVC_NvdbparsePsn(const char *psn);
const char *nvdbSysDtManufacturerName(char code);
int32_t nvdbSysDtYear(uint8_t code);
const char *nvdbSysDtMonth(uint8_t code);
void nvdbSysDtMarkLegacyPsn(void);
void nvdbSysDtResetAging(void);
int32_t SVC_ReadPSNFromOTP(char *psn, int32_t *slot);
int32_t SVC_WritePSNToOTP(const char *psn);

/* service_nvdb_product_mode.c */
void set_product_mode(uint8_t mode);
void productModeUpdate(uint8_t mode);
uint8_t productModeRead(void);

/* service_nvdb_sensor_caldata.c */
int32_t nvdbSensorCaldataAgRead(float accel[3], float gyro[3], float matrix[9]);
void nvdbSensorCaldataAgUpdate(const float *accel, const float *gyro, const float *matrix);

/* service_nvdb_buzzer.c */
uint32_t nvdbBuzzerFrequencyGet(void);
uint8_t nvdbBuzzerDutyGet(void);
void nvdbBuzzerUpdate(uint32_t frequency, uint8_t duty);

/* service_nvdb_mac.c */
void nvdbMacUpdate(const uint8_t *mac);
void nvdbAdvMagicUpdate(uint8_t magic);

#endif
