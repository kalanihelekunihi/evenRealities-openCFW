/* Stock 0x4eddc: report the latest activity accumulator snapshot. */
#include <stdint.h>
#include "native_activity_accumulator.h"
#include "../board/native_battery_memory.h"

extern void r1_eat_respond_format(const char *format, ...);

void r1_eat_callback_0004eddc(char *argument)
{
    (void)argument;
    _Alignas(4) uint8_t record[8];
    r1_activity_accumulator_latest_copy(record);
    r1_eat_respond_format("all_kcal:%d, steps:%d, kcal:%d\n",
                          read16(record + 4), read32(record),
                          read16(record + 6));
}
