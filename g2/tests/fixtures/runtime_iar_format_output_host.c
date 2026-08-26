/* Host composition for the source-owned IAR formatted-output adapter. */

#include <stdarg.h>
#include <stdint.h>

#include "../../components/apollo_main/core_overlay/runtime_format_parse_helpers.c"
#include "../../components/apollo_main/core_overlay/runtime_format_out_reverse.c"
#include "../../components/apollo_main/core_overlay/runtime_ntoa_format.c"

#define OPEN_CFW_RUNTIME_NTOA_DIVMOD_U64(value, base, result) \
    do { \
        (result)->quotient_low = (unsigned int)((value) / (base)); \
        (result)->quotient_high = \
            (unsigned int)(((value) / (base)) >> 32U); \
        (result)->remainder_low = (unsigned int)((value) % (base)); \
        (result)->remainder_high = 0U; \
    } while (0)
#include "../../components/apollo_main/core_overlay/runtime_ntoa_integer.c"
#undef OPEN_CFW_RUNTIME_NTOA_DIVMOD_U64

#include "../../components/apollo_main/core_overlay/runtime_bounded_string_length.c"
#include "../../components/apollo_main/core_overlay/runtime_strnlen_s.c"
#include "../../components/apollo_main/core_overlay/runtime_etoa.c"
#include "../../components/apollo_main/core_overlay/runtime_ftoa.c"

static void open_cfw_test_iar_noop(
    char character,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length
)
{
    open_cfw_runtime_noop_output(
        (unsigned char)character,
        (unsigned char *)buffer,
        index,
        maximum_length
    );
}

#define OPEN_CFW_RUNTIME_VSNPRINTF_NOOP_OUTPUT open_cfw_test_iar_noop
#define OPEN_CFW_RUNTIME_VSNPRINTF_STRING_LENGTH(string, maximum_length) \
    open_cfw_runtime_strnlen_s((string), (maximum_length))
#define OPEN_CFW_RUNTIME_VSNPRINTF_FUNCTION \
    open_cfw_runtime_iar_vsnprintf_engine
#define OPEN_CFW_RUNTIME_VSNPRINTF_ENABLE_COUNT 1
#define OPEN_CFW_RUNTIME_VSNPRINTF_ENABLE_HEXFLOAT 1
#define OPEN_CFW_RUNTIME_VSNPRINTF_ENABLE_IAR_LENGTHS 1
#include "../../components/apollo_main/core_overlay/runtime_vsnprintf.c"

#include "../../components/shared/runtime/runtime_iar_format_output.c"

unsigned char open_cfw_test_iar_output[256];
unsigned int open_cfw_test_iar_output_count;
unsigned int open_cfw_test_iar_output_fail_after;

static void *open_cfw_test_iar_writer(void *state, unsigned int character)
{
    (void)state;
    if (open_cfw_test_iar_output_count >= open_cfw_test_iar_output_fail_after) {
        return (void *)0;
    }
    open_cfw_test_iar_output[open_cfw_test_iar_output_count++] =
        (unsigned char)character;
    return (void *)(uintptr_t)1U;
}

void open_cfw_test_iar_output_reset(unsigned int fail_after)
{
    unsigned int index;

    open_cfw_test_iar_output_count = 0U;
    open_cfw_test_iar_output_fail_after = fail_after;
    for (index = 0U; index < sizeof(open_cfw_test_iar_output); index += 1U) {
        open_cfw_test_iar_output[index] = 0xCCU;
    }
}

static int open_cfw_test_iar_output_invoke(
    int secure,
    const unsigned char *format,
    ...
)
{
    va_list supplied;
    int observed;

    va_start(supplied, format);
    observed = open_cfw_runtime_iar_vformat(
        open_cfw_test_iar_writer,
        (void *)(uintptr_t)1U,
        format,
        supplied,
        secure
    );
    va_end(supplied);
    return observed;
}

int open_cfw_test_iar_output_standard(
    const char *text,
    int number,
    unsigned int hex,
    double real,
    int *count,
    int secure
)
{
    return open_cfw_test_iar_output_invoke(
        secure,
        (const unsigned char *)"%s %d %#x %.2f%n!",
        text, number, hex, real, count
    );
}

int open_cfw_test_iar_output_embedded_nul(int character)
{
    return open_cfw_test_iar_output_invoke(
        0, (const unsigned char *)"A%cB", character
    );
}

int open_cfw_test_iar_output_hexfloat(double value, const char *format)
{
    return open_cfw_test_iar_output_invoke(
        0, (const unsigned char *)format, value
    );
}

int open_cfw_test_iar_output_q(long long value)
{
    return open_cfw_test_iar_output_invoke(
        0, (const unsigned char *)"%qd", value
    );
}
