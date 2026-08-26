#include "../../components/bootloader/core_overlay/runtime_udiv10.c"
#include "../../components/bootloader/core_overlay/runtime_udec_digits.c"
#include "../../components/bootloader/core_overlay/runtime_sdec_digits.c"
#include "../../components/bootloader/core_overlay/runtime_hex_digits.c"
#include "../../components/bootloader/core_overlay/runtime_parse_dec.c"
#include "../../components/bootloader/core_overlay/runtime_u64_to_dec.c"
#include "../../components/bootloader/core_overlay/runtime_u64_to_hex.c"
#include "../../components/bootloader/core_overlay/runtime_nullable_strlen.c"
#include "../../components/bootloader/core_overlay/runtime_repeat_char.c"
#include "../../components/bootloader/core_overlay/runtime_float_to_fixed.c"

uint32_t open_cfw_bootloader_udec_digits_fixture(uint64_t value) { return open_cfw_bootloader_udec_digits(value); }
uint32_t open_cfw_bootloader_sdec_digits_fixture(int64_t value) { return open_cfw_bootloader_sdec_digits(value); }
uint32_t open_cfw_bootloader_hex_digits_fixture(uint64_t value) { return open_cfw_bootloader_hex_digits(value); }
int32_t open_cfw_bootloader_parse_dec_fixture(const char *text, uint32_t *consumed) { return open_cfw_bootloader_parse_dec(text, consumed); }
uint32_t open_cfw_bootloader_u64_to_dec_fixture(uint64_t value, char *output) { return open_cfw_bootloader_u64_to_dec(value, output); }
uint32_t open_cfw_bootloader_u64_to_hex_fixture(uint64_t value, char *output, uint32_t lowercase) { return open_cfw_bootloader_u64_to_hex(value, output, lowercase); }
uint32_t open_cfw_bootloader_nullable_strlen_fixture(const char *text) { return open_cfw_bootloader_nullable_strlen(text); }
uint32_t open_cfw_bootloader_repeat_char_fixture(char *output, uint32_t character, int32_t count) { return open_cfw_bootloader_repeat_char(output, character, count); }
int32_t open_cfw_bootloader_float_to_fixed_fixture(char *output, int32_t precision, float value) { return open_cfw_bootloader_float_to_fixed(output, precision, value); }
