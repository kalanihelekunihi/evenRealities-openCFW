/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room behavioral reconstruction of the G2
 * service_nvdb_sys_dt.c object.  The stock object owns the 172-byte
 * factory/system record plus the eight-slot OTP product-serial journal.
 */

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint8_t version;
    char product_serial[15];
    char board_serial[22];
    uint16_t crc16;
    uint32_t lux_base;
    uint8_t canvas_x;
    uint8_t canvas_y;
    uint8_t panel_current;
    uint8_t reserved_2f;
    uint8_t aging_start_time[40];
    uint8_t aging_end_time[40];
    uint8_t aging_soc_to_10_time[40];
    uint8_t aging_wrong_touch_times;
    uint8_t aging_begin_charge_soc;
    uint8_t aging_total_times;
    uint8_t aging_finish_flag;
} open_cfw_nvdb_sys_dt_record;

_Static_assert(sizeof(open_cfw_nvdb_sys_dt_record) == 172,
    "stock nvSysDt record must remain 172 bytes");
_Static_assert(offsetof(open_cfw_nvdb_sys_dt_record, product_serial) == 1,
    "stock product-serial offset changed");
_Static_assert(offsetof(open_cfw_nvdb_sys_dt_record, board_serial) == 16,
    "stock board-serial offset changed");
_Static_assert(offsetof(open_cfw_nvdb_sys_dt_record, crc16) == 38,
    "stock CRC offset changed");
_Static_assert(offsetof(open_cfw_nvdb_sys_dt_record, lux_base) == 40,
    "stock lux-base offset changed");
_Static_assert(offsetof(open_cfw_nvdb_sys_dt_record, aging_start_time) == 48,
    "stock aging-start offset changed");
_Static_assert(offsetof(open_cfw_nvdb_sys_dt_record, aging_finish_flag) == 171,
    "stock aging-finish offset changed");

enum {
    OPEN_CFW_NVDB_SYS_DT_PRODUCT_SERIAL = 0,
    OPEN_CFW_NVDB_SYS_DT_BOARD_SERIAL = 1,
    OPEN_CFW_NVDB_SYS_DT_LUX_BASE = 2,
    OPEN_CFW_NVDB_SYS_DT_CANVAS_X = 3,
    OPEN_CFW_NVDB_SYS_DT_CANVAS_Y = 4,
    OPEN_CFW_NVDB_SYS_DT_PANEL_CURRENT = 5,
    OPEN_CFW_NVDB_SYS_DT_AGING_START_TIME = 6,
    OPEN_CFW_NVDB_SYS_DT_AGING_END_TIME = 7,
    OPEN_CFW_NVDB_SYS_DT_AGING_SOC_TO_10_TIME = 8,
    OPEN_CFW_NVDB_SYS_DT_AGING_WRONG_TOUCH_TIMES = 9,
    OPEN_CFW_NVDB_SYS_DT_AGING_BEGIN_CHARGE_SOC = 10,
    OPEN_CFW_NVDB_SYS_DT_AGING_TOTAL_TIMES = 11,
    OPEN_CFW_NVDB_SYS_DT_AGING_FINISH_FLAG = 12,
    OPEN_CFW_NVDB_SYS_DT_FULL_RECORD = 13,
};

#ifndef OPEN_CFW_NVDB_SYS_DT_RECORD_ADDRESS
#define OPEN_CFW_NVDB_SYS_DT_RECORD_ADDRESS 0x20003994u
#endif
#ifndef OPEN_CFW_NVDB_SYS_DT_OTP_PSN_ADDRESS
#define OPEN_CFW_NVDB_SYS_DT_OTP_PSN_ADDRESS 0x20073EE4u
#endif
#ifndef OPEN_CFW_NVDB_SYS_DT_MONTH_BUFFER_ADDRESS
#define OPEN_CFW_NVDB_SYS_DT_MONTH_BUFFER_ADDRESS 0x200740B0u
#endif
#ifndef OPEN_CFW_NVDB_SYS_DT_LEGACY_PSN_FLAG_ADDRESS
#define OPEN_CFW_NVDB_SYS_DT_LEGACY_PSN_FLAG_ADDRESS 0x2007501Au
#endif
#ifndef OPEN_CFW_NVDB_SYS_DT_KEY
#define OPEN_CFW_NVDB_SYS_DT_KEY ((const char *)0x0078E63Cu)
#endif

#ifndef OPEN_CFW_NVDB_SYS_DT_CRC16
uint16_t open_cfw_crc16_ccitt(
    const uint8_t *data,
    uint32_t length,
    const uint16_t *seed
);
#define OPEN_CFW_NVDB_SYS_DT_CRC16(data, length, seed) \
    open_cfw_crc16_ccitt((data), (length), (seed))
#endif

#ifndef OPEN_CFW_NVDB_SYS_DT_READ
int open_cfw_nvdb_sys_dt_db_read(
    const char *key,
    void *value,
    uint16_t length
);
#define OPEN_CFW_NVDB_SYS_DT_READ(key, value, length) \
    open_cfw_nvdb_sys_dt_db_read((key), (value), (length))
#endif

#ifndef OPEN_CFW_NVDB_SYS_DT_WRITE
int open_cfw_nvdb_sys_dt_db_write(
    const char *key,
    const void *value,
    uint16_t length
);
#define OPEN_CFW_NVDB_SYS_DT_WRITE(key, value, length) \
    open_cfw_nvdb_sys_dt_db_write((key), (value), (length))
#endif

#ifndef OPEN_CFW_NVDB_SYS_DT_OTP_BEGIN
void open_cfw_nvdb_sys_dt_otp_begin(void);
#define OPEN_CFW_NVDB_SYS_DT_OTP_BEGIN() open_cfw_nvdb_sys_dt_otp_begin()
#endif
#ifndef OPEN_CFW_NVDB_SYS_DT_OTP_END
void open_cfw_nvdb_sys_dt_otp_end(void);
#define OPEN_CFW_NVDB_SYS_DT_OTP_END() open_cfw_nvdb_sys_dt_otp_end()
#endif
#ifndef OPEN_CFW_NVDB_SYS_DT_OTP_READ_WORD
int open_cfw_nvdb_sys_dt_otp_read_word(uint32_t offset, uint32_t *value);
#define OPEN_CFW_NVDB_SYS_DT_OTP_READ_WORD(offset, value) \
    open_cfw_nvdb_sys_dt_otp_read_word((offset), (value))
#endif
#ifndef OPEN_CFW_NVDB_SYS_DT_OTP_WRITE_WORD
int open_cfw_nvdb_sys_dt_otp_write_word(uint32_t offset, uint32_t value);
#define OPEN_CFW_NVDB_SYS_DT_OTP_WRITE_WORD(offset, value) \
    open_cfw_nvdb_sys_dt_otp_write_word((offset), (value))
#endif

#ifndef OPEN_CFW_NVDB_SYS_DT_PARSED
void open_cfw_nvdb_sys_dt_parsed(
    const char *project_code,
    char manufacturer_code,
    const char *manufacturer,
    char color,
    char year_code,
    uint32_t year,
    char month_code,
    const char *month,
    const char *day,
    const char *serial_number
);
#define OPEN_CFW_NVDB_SYS_DT_PARSED(...) \
    open_cfw_nvdb_sys_dt_parsed(__VA_ARGS__)
#endif

#ifndef OPEN_CFW_NVDB_SYS_DT_DIAGNOSTIC
#define OPEN_CFW_NVDB_SYS_DT_DIAGNOSTIC() ((void)0)
#endif

#define OPEN_CFW_NVDB_SYS_DT_RECORD \
    ((volatile open_cfw_nvdb_sys_dt_record *)(uintptr_t) \
        OPEN_CFW_NVDB_SYS_DT_RECORD_ADDRESS)
#define OPEN_CFW_NVDB_SYS_DT_OTP_PSN \
    ((volatile char *)(uintptr_t)OPEN_CFW_NVDB_SYS_DT_OTP_PSN_ADDRESS)
#define OPEN_CFW_NVDB_SYS_DT_MONTH_BUFFER \
    ((volatile char *)(uintptr_t)OPEN_CFW_NVDB_SYS_DT_MONTH_BUFFER_ADDRESS)
#define OPEN_CFW_NVDB_SYS_DT_LEGACY_PSN_FLAG \
    (*(volatile uint8_t *)(uintptr_t) \
        OPEN_CFW_NVDB_SYS_DT_LEGACY_PSN_FLAG_ADDRESS)

#ifndef OPEN_CFW_NVDB_SYS_DT_LEGACY_PSNS
static const char *const open_cfw_nvdb_sys_dt_legacy_psns[40] = {
    "S200LABI270028", "S200LABI270036", "S200LABI270050",
    "S200LDBE210004", "S200LABI260010", "S200LABI270068",
    "S200LABI270066", "S200LABI270004", "S200LABI270072",
    "S200LABI260003", "S200LABI250030", "S200LABI260024",
    "S200LABI260026", "S200LABI260021", "S200LABI270029",
    "S200LABI270058", "S200LABI270022", "S200LABI270073",
    "S200LABI250002", "S200LABI270071", "S200LABI270001",
    "S200LABI270012", "S200LABI260014", "S200LABI270027",
    "S200LABI270069", "S200LABI260009", "S200LABI270008",
    "S200LABI270060", "S200LABI270053", "S200LABI250023",
    "S200LABI270043", "S200LABG190017", "S200LCBI190019",
    "S200LCBI200013", "S200LABI270031", "S200LCBI200010",
    "S200LCBI200008", "S200LCBI190022", "S200LCBI200001",
    "S200LCBI190025",
};
#define OPEN_CFW_NVDB_SYS_DT_LEGACY_PSNS open_cfw_nvdb_sys_dt_legacy_psns
#endif

static void open_cfw_nvdb_sys_dt_copy(
    volatile void *destination,
    const volatile void *source,
    uint32_t length
)
{
    volatile uint8_t *out = (volatile uint8_t *)destination;
    const volatile uint8_t *in = (const volatile uint8_t *)source;
    uint32_t index;

    for (index = 0; index < length; ++index) {
        out[index] = in[index];
    }
}

static void open_cfw_nvdb_sys_dt_zero(volatile void *destination, uint32_t length)
{
    volatile uint8_t *out = (volatile uint8_t *)destination;
    uint32_t index;

    for (index = 0; index < length; ++index) {
        out[index] = 0u;
    }
}

static uint32_t open_cfw_nvdb_sys_dt_string_length(const char *value)
{
    uint32_t length = 0;
    while (value[length] != '\0') {
        ++length;
    }
    return length;
}

static int open_cfw_nvdb_sys_dt_string_equal_n(
    const char *left,
    const char *right,
    uint32_t length
)
{
    uint32_t index;
    for (index = 0; index < length; ++index) {
        uint8_t a = (uint8_t)left[index];
        uint8_t b = (uint8_t)right[index];
        if (a != b) {
            return 0;
        }
        if (a == 0u) {
            return 1;
        }
    }
    return 1;
}

static int open_cfw_nvdb_sys_dt_valid_psn(const char *value)
{
    uint32_t index;
    if (value[0] != 'S' || value[1] != '2') {
        return 0;
    }
    for (index = 8; index < 14; ++index) {
        if (value[index] < '0' || value[index] > '9') {
            return 0;
        }
    }
    return 1;
}

static uint16_t open_cfw_nvdb_sys_dt_crc(void)
{
    return OPEN_CFW_NVDB_SYS_DT_CRC16(
        (const uint8_t *)(uintptr_t)OPEN_CFW_NVDB_SYS_DT_RECORD,
        38u,
        (const uint16_t *)0
    );
}

__attribute__((used, noinline))
int open_cfw_nvdb_sys_dt_default_initialize(void)
{
    OPEN_CFW_NVDB_SYS_DT_RECORD->crc16 = open_cfw_nvdb_sys_dt_crc();
    return 0;
}

void open_cfw_nvdb_sys_dt_parse_psn(const char *product_serial);
void open_cfw_nvdb_sys_dt_mark_legacy_psn(void);
int open_cfw_nvdb_sys_dt_read_psn_from_otp(char *output, int *slot_index);
int open_cfw_nvdb_sys_dt_write(uint8_t data_index, const void *data);

__attribute__((used, noinline))
int open_cfw_nvdb_sys_dt_load_and_migrate(void)
{
    open_cfw_nvdb_sys_dt_record stored;
    volatile open_cfw_nvdb_sys_dt_record *record = OPEN_CFW_NVDB_SYS_DT_RECORD;
    volatile char *otp_psn = OPEN_CFW_NVDB_SYS_DT_OTP_PSN;
    int result;

    OPEN_CFW_NVDB_SYS_DT_DIAGNOSTIC();
    record->product_serial[14] = '\0';
    open_cfw_nvdb_sys_dt_parse_psn(
        (const char *)(uintptr_t)&record->product_serial[0]
    );
    result = OPEN_CFW_NVDB_SYS_DT_READ(
        OPEN_CFW_NVDB_SYS_DT_KEY,
        &stored,
        (uint16_t)sizeof(stored)
    );
    open_cfw_nvdb_sys_dt_mark_legacy_psn();
    if (open_cfw_nvdb_sys_dt_read_psn_from_otp(
            (char *)(uintptr_t)otp_psn,
            (int *)0) == 0) {
        open_cfw_nvdb_sys_dt_copy(
            record->product_serial,
            otp_psn,
            14u
        );
        record->product_serial[14] = '\0';
    }
    if (result >= 1) {
        if (stored.crc16 != record->crc16 && stored.version < 2u) {
            (void)open_cfw_nvdb_sys_dt_write(
                OPEN_CFW_NVDB_SYS_DT_PRODUCT_SERIAL,
                (const void *)(uintptr_t)&record->product_serial[0]
            );
        }
    } else {
        (void)open_cfw_nvdb_sys_dt_write(
            OPEN_CFW_NVDB_SYS_DT_PRODUCT_SERIAL,
            (const void *)(uintptr_t)&record->product_serial[0]
        );
    }
    return 0;
}

__attribute__((used, noinline))
int open_cfw_nvdb_sys_dt_write(uint8_t data_index, const void *data)
{
    volatile open_cfw_nvdb_sys_dt_record *record = OPEN_CFW_NVDB_SYS_DT_RECORD;
    uint32_t length;
    int valid = 0;

    switch (data_index) {
    case OPEN_CFW_NVDB_SYS_DT_PRODUCT_SERIAL:
        if (data != (const void *)0) {
            length = open_cfw_nvdb_sys_dt_string_length((const char *)data);
            if (length > 14u) {
                length = 14u;
            }
            open_cfw_nvdb_sys_dt_copy(
                record->product_serial,
                data,
                length
            );
            record->product_serial[length] = '\0';
            valid = 1;
        }
        break;
    case OPEN_CFW_NVDB_SYS_DT_BOARD_SERIAL:
        if (data != (const void *)0) {
            length = open_cfw_nvdb_sys_dt_string_length((const char *)data);
            if (length > 21u) {
                length = 21u;
            }
            open_cfw_nvdb_sys_dt_copy(record->board_serial, data, length);
            record->board_serial[length] = '\0';
            valid = 1;
        }
        break;
    case OPEN_CFW_NVDB_SYS_DT_LUX_BASE:
        if (data != (const void *)0) {
            open_cfw_nvdb_sys_dt_copy(&record->lux_base, data, 4u);
            valid = 1;
        }
        break;
    case OPEN_CFW_NVDB_SYS_DT_CANVAS_X:
        if (data != (const void *)0) {
            record->canvas_x = *(const uint8_t *)data;
            valid = 1;
        }
        break;
    case OPEN_CFW_NVDB_SYS_DT_CANVAS_Y:
        if (data != (const void *)0) {
            record->canvas_y = *(const uint8_t *)data;
            valid = 1;
        }
        break;
    case OPEN_CFW_NVDB_SYS_DT_PANEL_CURRENT:
        if (data != (const void *)0) {
            record->panel_current = *(const uint8_t *)data;
            valid = 1;
        }
        break;
    case OPEN_CFW_NVDB_SYS_DT_AGING_START_TIME:
        if (data != (const void *)0) {
            open_cfw_nvdb_sys_dt_copy(record->aging_start_time, data, 40u);
            valid = 1;
        }
        break;
    case OPEN_CFW_NVDB_SYS_DT_AGING_END_TIME:
        if (data != (const void *)0) {
            open_cfw_nvdb_sys_dt_copy(record->aging_end_time, data, 40u);
            valid = 1;
        }
        break;
    case OPEN_CFW_NVDB_SYS_DT_AGING_SOC_TO_10_TIME:
        if (data != (const void *)0) {
            open_cfw_nvdb_sys_dt_copy(
                record->aging_soc_to_10_time,
                data,
                40u
            );
            valid = 1;
        }
        break;
    case OPEN_CFW_NVDB_SYS_DT_AGING_WRONG_TOUCH_TIMES:
        if (data != (const void *)0) {
            record->aging_wrong_touch_times = *(const uint8_t *)data;
            valid = 1;
        }
        break;
    case OPEN_CFW_NVDB_SYS_DT_AGING_BEGIN_CHARGE_SOC:
        if (data != (const void *)0) {
            record->aging_begin_charge_soc = *(const uint8_t *)data;
            valid = 1;
        }
        break;
    case OPEN_CFW_NVDB_SYS_DT_AGING_TOTAL_TIMES:
        if (data != (const void *)0) {
            record->aging_total_times = *(const uint8_t *)data;
            valid = 1;
        }
        break;
    case OPEN_CFW_NVDB_SYS_DT_AGING_FINISH_FLAG:
        if (data != (const void *)0) {
            record->aging_finish_flag = *(const uint8_t *)data;
            valid = 1;
        }
        break;
    case OPEN_CFW_NVDB_SYS_DT_FULL_RECORD:
        if (data != (const void *)0) {
            open_cfw_nvdb_sys_dt_copy(record, data, sizeof(*record));
            valid = 1;
        }
        break;
    default:
        break;
    }

    if (!valid) {
        return 0;
    }
    record->version = 2u;
    record->crc16 = open_cfw_nvdb_sys_dt_crc();
    return OPEN_CFW_NVDB_SYS_DT_WRITE(
        OPEN_CFW_NVDB_SYS_DT_KEY,
        (const void *)(uintptr_t)record,
        (uint16_t)sizeof(*record)
    );
}

__attribute__((used, noinline))
void *open_cfw_nvdb_sys_dt_get(uint8_t data_index)
{
    volatile open_cfw_nvdb_sys_dt_record *record = OPEN_CFW_NVDB_SYS_DT_RECORD;

    switch (data_index) {
    case OPEN_CFW_NVDB_SYS_DT_PRODUCT_SERIAL:
        return (void *)(uintptr_t)&record->product_serial[0];
    case OPEN_CFW_NVDB_SYS_DT_BOARD_SERIAL:
        return (void *)(uintptr_t)&record->board_serial[0];
    case OPEN_CFW_NVDB_SYS_DT_LUX_BASE:
        return (void *)(uintptr_t)&record->lux_base;
    case OPEN_CFW_NVDB_SYS_DT_CANVAS_X:
        return (void *)(uintptr_t)&record->canvas_x;
    case OPEN_CFW_NVDB_SYS_DT_CANVAS_Y:
        return (void *)(uintptr_t)&record->canvas_y;
    case OPEN_CFW_NVDB_SYS_DT_PANEL_CURRENT:
        return (void *)(uintptr_t)&record->panel_current;
    case OPEN_CFW_NVDB_SYS_DT_AGING_START_TIME:
        return (void *)(uintptr_t)&record->aging_start_time[0];
    case OPEN_CFW_NVDB_SYS_DT_AGING_END_TIME:
        return (void *)(uintptr_t)&record->aging_end_time[0];
    case OPEN_CFW_NVDB_SYS_DT_AGING_SOC_TO_10_TIME:
        return (void *)(uintptr_t)&record->aging_soc_to_10_time[0];
    case OPEN_CFW_NVDB_SYS_DT_AGING_WRONG_TOUCH_TIMES:
        return (void *)(uintptr_t)&record->aging_wrong_touch_times;
    case OPEN_CFW_NVDB_SYS_DT_AGING_BEGIN_CHARGE_SOC:
        return (void *)(uintptr_t)&record->aging_begin_charge_soc;
    case OPEN_CFW_NVDB_SYS_DT_AGING_TOTAL_TIMES:
        return (void *)(uintptr_t)&record->aging_total_times;
    case OPEN_CFW_NVDB_SYS_DT_AGING_FINISH_FLAG:
        return (void *)(uintptr_t)&record->aging_finish_flag;
    default:
        return (void *)(uintptr_t)record;
    }
}

__attribute__((used, noinline))
void *open_cfw_nvdb_sys_dt_read(uint8_t data_index)
{
    volatile open_cfw_nvdb_sys_dt_record *record = OPEN_CFW_NVDB_SYS_DT_RECORD;
    volatile char *otp_psn = OPEN_CFW_NVDB_SYS_DT_OTP_PSN;

    (void)OPEN_CFW_NVDB_SYS_DT_READ(
        OPEN_CFW_NVDB_SYS_DT_KEY,
        (void *)(uintptr_t)record,
        (uint16_t)sizeof(*record)
    );
    open_cfw_nvdb_sys_dt_mark_legacy_psn();
    if (open_cfw_nvdb_sys_dt_read_psn_from_otp(
            (char *)(uintptr_t)otp_psn,
            (int *)0) == 0) {
        open_cfw_nvdb_sys_dt_copy(
            record->product_serial,
            otp_psn,
            14u
        );
        record->product_serial[14] = '\0';
    }
    return open_cfw_nvdb_sys_dt_get(data_index);
}

const char *open_cfw_nvdb_sys_dt_manufacturer_name(char code);
uint32_t open_cfw_nvdb_sys_dt_year(char code);
const char *open_cfw_nvdb_sys_dt_month(char code);

__attribute__((used, noinline))
void open_cfw_nvdb_sys_dt_parse_psn(const char *product_serial)
{
    char project_code[5];
    char day[3];
    char serial_number[5];
    char manufacturer_code;
    char color;
    char year_code;
    char month_code;

    if (open_cfw_nvdb_sys_dt_string_length(product_serial) < 14u) {
        OPEN_CFW_NVDB_SYS_DT_DIAGNOSTIC();
        return;
    }
    open_cfw_nvdb_sys_dt_copy(project_code, product_serial, 4u);
    project_code[4] = '\0';
    manufacturer_code = product_serial[4];
    color = product_serial[5];
    year_code = product_serial[6];
    month_code = product_serial[7];
    open_cfw_nvdb_sys_dt_copy(day, product_serial + 8, 2u);
    day[2] = '\0';
    open_cfw_nvdb_sys_dt_copy(serial_number, product_serial + 10, 4u);
    serial_number[4] = '\0';
    OPEN_CFW_NVDB_SYS_DT_PARSED(
        project_code,
        manufacturer_code,
        open_cfw_nvdb_sys_dt_manufacturer_name(manufacturer_code),
        color,
        year_code,
        open_cfw_nvdb_sys_dt_year(year_code),
        month_code,
        open_cfw_nvdb_sys_dt_month(month_code),
        day,
        serial_number
    );
}

__attribute__((used, noinline))
const char *open_cfw_nvdb_sys_dt_manufacturer_name(char code)
{
    return code == 'L' ? "LianHeGuangDian" : "unknow";
}

__attribute__((used, noinline))
uint32_t open_cfw_nvdb_sys_dt_year(char code)
{
    uint8_t value = (uint8_t)code;
    return value >= (uint8_t)'A' && value <= (uint8_t)'Z'
        ? (uint32_t)value + 1959u
        : 0u;
}

__attribute__((used, noinline))
const char *open_cfw_nvdb_sys_dt_month(char code)
{
    volatile char *buffer = OPEN_CFW_NVDB_SYS_DT_MONTH_BUFFER;
    uint8_t value = (uint8_t)code;
    uint32_t month;

    if (value < (uint8_t)'A' || value > (uint8_t)'Z') {
        return "unknow";
    }
    month = (uint32_t)(value - (uint8_t)'@');
    if (month >= 10u) {
        buffer[0] = (char)('0' + month / 10u);
        buffer[1] = (char)('0' + month % 10u);
        buffer[2] = '\0';
    } else {
        buffer[0] = (char)('0' + month);
        buffer[1] = '\0';
    }
    return (const char *)(uintptr_t)buffer;
}

__attribute__((used, noinline))
void open_cfw_nvdb_sys_dt_reset_aging(void)
{
    volatile open_cfw_nvdb_sys_dt_record *record = OPEN_CFW_NVDB_SYS_DT_RECORD;

    open_cfw_nvdb_sys_dt_zero(record->aging_start_time, 40u);
    open_cfw_nvdb_sys_dt_zero(record->aging_end_time, 40u);
    open_cfw_nvdb_sys_dt_zero(record->aging_soc_to_10_time, 40u);
    record->aging_wrong_touch_times = 0u;
    record->aging_begin_charge_soc = 0u;
    record->aging_finish_flag = 0u;
    (void)open_cfw_nvdb_sys_dt_write(
        OPEN_CFW_NVDB_SYS_DT_AGING_BEGIN_CHARGE_SOC,
        (const void *)(uintptr_t)&record->aging_begin_charge_soc
    );
}

__attribute__((used, noinline))
void open_cfw_nvdb_sys_dt_mark_legacy_psn(void)
{
    volatile open_cfw_nvdb_sys_dt_record *record = OPEN_CFW_NVDB_SYS_DT_RECORD;
    uint32_t index;

    for (index = 0; index < 40u; ++index) {
        if (open_cfw_nvdb_sys_dt_string_equal_n(
                (const char *)(uintptr_t)&record->product_serial[0],
                OPEN_CFW_NVDB_SYS_DT_LEGACY_PSNS[index],
                15u)) {
            OPEN_CFW_NVDB_SYS_DT_LEGACY_PSN_FLAG = 1u;
            return;
        }
    }
}

__attribute__((used, noinline))
int open_cfw_nvdb_sys_dt_read_psn_from_otp(char *output, int *slot_index)
{
    uint8_t slot[16];
    char candidate[15];
    int latest = -1;
    uint32_t slot_number;
    uint32_t word_index;
    int failed = 0;

    OPEN_CFW_NVDB_SYS_DT_OTP_BEGIN();
    for (slot_number = 0; slot_number < 8u; ++slot_number) {
        open_cfw_nvdb_sys_dt_zero(slot, sizeof(slot));
        for (word_index = 0; word_index < 4u; ++word_index) {
            if (OPEN_CFW_NVDB_SYS_DT_OTP_READ_WORD(
                    0x340u + slot_number * 16u + word_index * 4u,
                    (uint32_t *)(void *)(slot + word_index * 4u)) != 0) {
                failed = 1;
                break;
            }
        }
        if (failed) {
            break;
        }
        open_cfw_nvdb_sys_dt_copy(candidate, slot, 14u);
        candidate[14] = '\0';
        if (open_cfw_nvdb_sys_dt_valid_psn(candidate)) {
            latest = (int)slot_number;
            open_cfw_nvdb_sys_dt_copy(output, candidate, 14u);
            output[14] = '\0';
        }
    }
    OPEN_CFW_NVDB_SYS_DT_OTP_END();

    if (latest < 0) {
        return -1;
    }
    if (slot_index != (int *)0) {
        *slot_index = latest;
    }
    return 0;
}

__attribute__((used, noinline))
int open_cfw_nvdb_sys_dt_write_psn_to_otp(const char *product_serial)
{
    char current[15];
    uint8_t slot[16];
    int latest = -1;
    int target;
    uint32_t word_index;

    if (product_serial == (const char *)0 ||
        !open_cfw_nvdb_sys_dt_valid_psn(product_serial)) {
        return -1;
    }
    if (open_cfw_nvdb_sys_dt_read_psn_from_otp(current, &latest) == 0) {
        if (open_cfw_nvdb_sys_dt_string_equal_n(
                current,
                product_serial,
                14u)) {
            return 0;
        }
        target = latest + 1;
    } else {
        target = 0;
    }
    if (target >= 8) {
        return -1;
    }

    open_cfw_nvdb_sys_dt_zero(slot, sizeof(slot));
    open_cfw_nvdb_sys_dt_copy(slot, product_serial, 14u);
    OPEN_CFW_NVDB_SYS_DT_OTP_BEGIN();
    for (word_index = 0; word_index < 4u; ++word_index) {
        uint32_t word =
            (uint32_t)slot[word_index * 4u] |
            ((uint32_t)slot[word_index * 4u + 1u] << 8) |
            ((uint32_t)slot[word_index * 4u + 2u] << 16) |
            ((uint32_t)slot[word_index * 4u + 3u] << 24);
        if (OPEN_CFW_NVDB_SYS_DT_OTP_WRITE_WORD(
                0x340u + (uint32_t)target * 16u + word_index * 4u,
                word) != 0) {
            OPEN_CFW_NVDB_SYS_DT_OTP_END();
            return -1;
        }
    }
    OPEN_CFW_NVDB_SYS_DT_OTP_END();
    return 0;
}
