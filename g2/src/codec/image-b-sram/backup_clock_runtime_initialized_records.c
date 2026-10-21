/* Image-B loaded clock runtime records at 0x100168c0..0x1001699b,
 * visible through the native 0x200... data alias.  The 10 record pairs
 * are consumed by clock init 0x10003294 and writer 0x100035a0.
 * The 60-byte state has authenticated initial words; +0x14 is changed by
 * clock trim and +0x38 marks the trim path.  Other field roles still need
 * a wider writer/reader census and are retained as indexed words.
 */
#include <stdint.h>

typedef struct { uint32_t selector; uint32_t value; } clock_record;
_Static_assert(sizeof(clock_record) == 8u, "clock record ABI");

__attribute__((section(".data.image_b.clock_state"), aligned(4)))
volatile uint32_t gx8002_image_b_clock_state_200168c0[15] = {
    1u, UINT32_C(0x00008000), UINT32_C(0x05dc0000),
    UINT32_C(0x02ee0000), 0u, UINT32_C(0x00000bff),
    2u, 0u, 3u, 0u, 0u, 4u, 0u, 0u, UINT32_C(0xffffffff),
};

__attribute__((section(".data.image_b.clock_boot_records"), aligned(4)))
volatile clock_record gx8002_image_b_clock_boot_records_200168fc[10] = {
    {15u, 0u}, {27u, 0u}, {28u, 0u}, {29u, 0u}, {26u, 1u},
    {16u, 1u}, {17u, 0u}, {18u, 1u}, {0u, 0u}, {14u, 0u},
};

__attribute__((section(".data.image_b.clock_trim_records"), aligned(4)))
volatile clock_record gx8002_image_b_clock_trim_records_2001694c[10] = {
    {15u, 0u}, {27u, 0u}, {28u, 0u}, {29u, 0u}, {26u, 0u},
    {16u, 0u}, {17u, 0u}, {18u, 1u}, {0u, 1u}, {14u, 0u},
};

/* The flash descriptor immediately precedes the initialized callback table.
 * Probe 0x10007c90 fills its runtime fields after reset. The stock load
 * image gives only the first sentinel and seven cleared words here. */
__attribute__((section(".data.image_b.flash_descriptor"), aligned(4)))
volatile uint32_t gx8002_image_b_flash_descriptor_20016d60[8] = {
    UINT32_C(0xffffffff), 0u, 0u, 0u, 0u, 0u, 0u, 0u,
};
