/*
 * SPDX-License-Identifier: MIT
 *
 * Wall-clock seconds and validity helper matched to stock entry 0x0047DCB4.
 */

typedef __UINTPTR_TYPE__ open_cfw_wall_time_uintptr;

typedef unsigned int (*open_cfw_wall_time_query_function)(void);

#ifndef OPEN_CFW_WALL_TIME_MODE
#define OPEN_CFW_WALL_TIME_MODE() \
    (((open_cfw_wall_time_query_function) \
        (open_cfw_wall_time_uintptr)0x0044906DU)())
#endif
#ifndef OPEN_CFW_WALL_TIME_SECONDS
#define OPEN_CFW_WALL_TIME_SECONDS() \
    (((open_cfw_wall_time_query_function) \
        (open_cfw_wall_time_uintptr)0x0044A1EBU)())
#endif

#define OPEN_CFW_WALL_TIME_VALID_BEGIN 1704067200U
#define OPEN_CFW_WALL_TIME_VALID_SPAN 2398377600U

__attribute__((used, noinline))
unsigned int open_cfw_wall_time_seconds(unsigned char *valid)
{
    unsigned int seconds;

    if (OPEN_CFW_WALL_TIME_MODE() != 2U) {
        *valid = 0U;
        return 0U;
    }

    seconds = OPEN_CFW_WALL_TIME_SECONDS();
    *valid = (unsigned char)(
        (seconds - OPEN_CFW_WALL_TIME_VALID_BEGIN)
        < OPEN_CFW_WALL_TIME_VALID_SPAN
    );
    return seconds;
}

#undef OPEN_CFW_WALL_TIME_VALID_SPAN
#undef OPEN_CFW_WALL_TIME_VALID_BEGIN
#undef OPEN_CFW_WALL_TIME_SECONDS
#undef OPEN_CFW_WALL_TIME_MODE
