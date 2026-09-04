/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "../../components/apollo_main/core_overlay/at_core.h"

static struct open_cfw_at_core_state g_state;
static char g_parser_buffer[768];
static int g_parser_init_calls;
static int g_adapt_calls;
static int g_direct_calls;
static int g_callback_calls[3];
static const char *g_segments[5];
static unsigned int g_segment_index;
static const char *g_parameter_1;
static const char *g_parameter_2;

static void callback_0(const char *message, int length)
{
    assert((int)strlen(message) == length);
    g_callback_calls[0] += 1;
}

static void callback_1(const char *message, int length)
{
    assert((int)strlen(message) == length);
    g_callback_calls[1] += 1;
}

static void callback_2(const char *message, int length)
{
    assert((int)strlen(message) == length);
    g_callback_calls[2] += 1;
}

static void direct_handler(const char *parameter_1, const char *parameter_2)
{
    g_direct_calls += 1;
    g_parameter_1 = parameter_1;
    g_parameter_2 = parameter_2;
}

static void host_parser_init(void)
{
    g_parser_init_calls += 1;
    open_cfw_at_core_register_callback(2, callback_2);
}

static char *host_parser_next(
    const char *input,
    const uint16_t *separators,
    char **cursor
)
{
    (void)input;
    assert(*separators == (uint16_t)'=');
    *cursor = (char *)g_segments;
    return (char *)g_segments[g_segment_index++];
}

static void host_parser_adapt(
    open_cfw_at_core_command_handler handler,
    const char *parameter_1,
    const char *parameter_2
)
{
    g_adapt_calls += 1;
    handler(parameter_1, parameter_2);
}

static int host_vsnprintf(
    unsigned char *buffer,
    unsigned int capacity,
    const unsigned char *format,
    va_list arguments
)
{
    return vsnprintf(
        (char *)buffer, capacity, (const char *)format, arguments
    );
}

static const struct open_cfw_at_core_command g_commands[] = {
    {0u, "AT^DIRECT", direct_handler, 0u},
    {2u, "AT^ADAPT", direct_handler, 0u},
    {0u, "AT^NULL", NULL, 0u},
};

#define OPEN_CFW_AT_CORE_STATE (&g_state)
#define OPEN_CFW_AT_CORE_COMMAND_TABLE (g_commands)
#define OPEN_CFW_AT_CORE_COMMAND_TABLE_END \
    ((uintptr_t)(g_commands + sizeof(g_commands) / sizeof(g_commands[0])))
#define OPEN_CFW_AT_CORE_PARSER_BUFFER (g_parser_buffer)
#define OPEN_CFW_AT_CORE_PARSER_INIT() host_parser_init()
#define OPEN_CFW_AT_CORE_PARSER_NEXT(input, separators, cursor) \
    host_parser_next((input), (separators), (cursor))
#define OPEN_CFW_AT_CORE_PARSER_ADAPT(handler, parameter_1, parameter_2) \
    host_parser_adapt((handler), (parameter_1), (parameter_2))
#define OPEN_CFW_AT_CORE_VSNPRINTF(buffer, capacity, format, arguments) \
    host_vsnprintf( \
        (unsigned char *)(buffer), (capacity), \
        (const unsigned char *)(format), (arguments) \
    )
#include "../../components/apollo_main/core_overlay/at_core.c"

static void reset_fixture(void)
{
    memset(&g_state, 0, sizeof(g_state));
    memset(g_parser_buffer, 0xa5, sizeof(g_parser_buffer));
    memset(g_callback_calls, 0, sizeof(g_callback_calls));
    memset(g_segments, 0, sizeof(g_segments));
    g_parser_init_calls = 0;
    g_adapt_calls = 0;
    g_direct_calls = 0;
    g_segment_index = 0;
    g_parameter_1 = NULL;
    g_parameter_2 = NULL;
}

int main(void)
{
    char long_command[257];

    reset_fixture();
    open_cfw_at_core_register_callback(3, callback_0);
    assert(g_state.callback_mask == 0u);
    open_cfw_at_core_register_callback(1, callback_1);
    assert(g_state.callback_mask == 2u);
    open_cfw_at_core_init();
    assert(g_parser_init_calls == 1);
    assert(g_state.commands == g_commands);
    assert(g_state.command_count == 3u);
    assert((g_state.flags & 3u) == 3u);
    assert((g_state.callback_mask & 4u) != 0u);

    open_cfw_at_core_dispatch_command("AT^DIRECT", "one", "two");
    assert(g_direct_calls == 1);
    assert(strcmp(g_parameter_1, "one") == 0);
    assert(strcmp(g_parameter_2, "two") == 0);
    open_cfw_at_core_dispatch_command("AT^ADAPT", "three", NULL);
    assert(g_adapt_calls == 1);
    assert(g_direct_calls == 2);
    open_cfw_at_core_dispatch_command("AT^MISSING", NULL, NULL);
    open_cfw_at_core_dispatch_command("AT^NULL", NULL, NULL);
    assert(g_direct_calls == 2);

    g_state.flags |= 4u;
    open_cfw_at_core_dispatch_command("AT^DIRECT", NULL, NULL);
    assert(g_direct_calls == 2);
    g_state.flags &= ~4u;
    g_state.flags = 0u;
    open_cfw_at_core_dispatch_command("AT^DIRECT", NULL, NULL);
    assert(g_direct_calls == 2);
    g_state.flags = 3u;
    memset(long_command, 'A', sizeof(long_command) - 1u);
    long_command[sizeof(long_command) - 1u] = '\0';
    open_cfw_at_core_dispatch_command(long_command, NULL, NULL);
    assert(g_direct_calls == 2);

    g_segments[0] = "AT^DIRECT";
    g_segments[1] = "left";
    g_segments[2] = "right";
    g_segments[3] = NULL;
    g_segment_index = 0;
    open_cfw_at_core_handler("ignored");
    assert(g_direct_calls == 3);
    assert(strcmp(g_parameter_1, "left") == 0);
    assert(strcmp(g_parameter_2, "right") == 0);

    g_state.output_mode = 0u;
    open_cfw_at_core_output("value=%d", 17);
    assert(strcmp(g_state.output, "value=17") == 0);
    assert(g_callback_calls[0] == 0);
    assert(g_callback_calls[1] == 1);
    assert(g_callback_calls[2] == 1);
    g_state.output_mode = 1u;
    open_cfw_at_core_output("%s", "one");
    assert(g_callback_calls[1] == 2);
    assert(g_callback_calls[2] == 1);
    g_state.output_mode = 2u;
    open_cfw_at_core_output("%s", "two");
    assert(g_callback_calls[2] == 2);
    g_state.output_mode = 3u;
    open_cfw_at_core_output("%s", "none");
    assert(g_callback_calls[1] == 2);
    assert(g_callback_calls[2] == 2);
    open_cfw_at_core_output("%s", "");
    assert(g_callback_calls[1] == 2);
    assert(g_callback_calls[2] == 2);

    return 0;
}
