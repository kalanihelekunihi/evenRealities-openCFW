/* SPDX-License-Identifier: MIT
 * Stock 0x004d3cf8, G2 2.2.6.10; REA review: g2/evidence/rtc-weekday-review.json.
 * Preserve the firmware's unusual leap predicate (including century behavior).
 * Return 7 for invalid inputs. Sunday=0. Arithmetic wraps as on the ARM target.
 */
#include <stdint.h>

uint32_t rtc_weekday_from_date_4d3cf8(uint32_t year, uint32_t month, uint32_t day)
{
    static const uint32_t days[12] = {31,28,31,30,31,30,31,31,30,31,30,31};
    static const uint32_t offsets[12] = {4,0,0,3,5,1,3,6,2,4,0,2};
    if (month - 1u >= 12u || (int32_t)year < 0 || (int32_t)day < 1)
        return 7;
    uint32_t leap = (year & 3u) == 0 && (year % 100u != 0 || year % 400u != 0);
    if (day > days[month - 1u] && !(month == 2 && leap && day == 29))
        return 7;
    uint32_t value = year / 4u + year + 2u - year / 100u + year / 400u;
    value += offsets[month - 1u] + day;
    if (leap && month < 3)
        value -= 1u;
    return (uint32_t)((int32_t)value % 7);
}
