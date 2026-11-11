/* Stock 0x91504: publish the product version through the typed log path. */
#include <stddef.h>
#include <stdint.h>

extern const char r1_device_info_firmware[];
extern int snprintf(char *, size_t, const char *, ...);
extern uint32_t r1_structured_log_typed(uint32_t, const char *, ...);

static int parse_four_decimal_fields(const char *cursor, int fields[4])
{
    for (unsigned index = 0; index < 4; ++index) {
        int value = 0;
        if (*cursor < '0' || *cursor > '9') return 0;
        do {
            int digit = *cursor++ - '0';
            if (value > (INT32_MAX - digit) / 10) return 0;
            value = value * 10 + digit;
        } while (*cursor >= '0' && *cursor <= '9');
        fields[index] = value;
        if (index != 3) {
            if (*cursor++ != '.') return 0;
        }
    }
    return 1;
}

void r1_manager_logging_start_91504(void)
{
    int fields[4] = {0};
    char label[16] = {0};

    if (parse_four_decimal_fields(r1_device_info_firmware, fields)) {
        (void)snprintf(label, sizeof(label), "VER%d%d%d%02d",
                       fields[0], fields[1], fields[2], fields[3] % 100);
    } else {
        (void)snprintf(label, sizeof(label), "VER%s", r1_device_info_firmware);
    }
    (void)r1_structured_log_typed(UINT32_C(0x8c400000), "%s", label);
}
