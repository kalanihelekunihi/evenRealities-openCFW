/* EAT commands that signal the existing protocol service thread. */
#include <stdint.h>

extern uint32_t r1_protocol_service_thread_flags_set(uint32_t flags);

void r1_eat_callback_0004f040(char *argument)
{
    (void)argument;
    (void)r1_protocol_service_thread_flags_set(4u);
}

void r1_eat_callback_0004eefc(char *argument)
{
    (void)argument;
    (void)r1_protocol_service_thread_flags_set(0x100u);
}

void r1_eat_callback_0004ef0a(char *argument)
{
    (void)argument;
    (void)r1_protocol_service_thread_flags_set(0x400u);
}

void r1_eat_callback_0004ef18(char *argument)
{
    (void)argument;
    (void)r1_protocol_service_thread_flags_set(0x80u);
}
