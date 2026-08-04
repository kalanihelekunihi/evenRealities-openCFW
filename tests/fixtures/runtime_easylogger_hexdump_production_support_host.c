/* Host-only execution harness for production EasyLogger hexdump leaves. */

#define OPEN_CFW_EASYLOGGER_HEXDUMP_LEAF_PUT 1
#define OPEN_CFW_EASYLOGGER_HEXDUMP_LEAF_PUT_HEX 1
#define OPEN_CFW_EASYLOGGER_HEXDUMP_LEAF_FORMAT_HEADER 1
#define OPEN_CFW_EASYLOGGER_HEXDUMP_LEAF_FORMAT_HEX 1

#include "../../components/apollo_main/core_overlay/runtime_easylogger_hexdump_support.c"

void open_cfw_test_easylogger_hexdump_production_format_hex(
    unsigned char value,
    char *output
)
{
    open_cfw_easylogger_hexdump_format_hex(output, value);
}

unsigned int open_cfw_test_easylogger_hexdump_production_put_hex(
    unsigned int value,
    unsigned int minimum_digits,
    char *output,
    unsigned int size
)
{
    open_cfw_easylogger_hexdump_seam_u32 length = 0U;
    open_cfw_easylogger_hexdump_put_hex(
        output,
        size,
        &length,
        value,
        minimum_digits
    );
    return length;
}

int open_cfw_test_easylogger_hexdump_production_format_header(
    char *output,
    unsigned int size,
    const char *name,
    unsigned int offset,
    unsigned int end
)
{
    return open_cfw_easylogger_hexdump_format_header(
        output,
        size,
        name,
        offset,
        end
    );
}
