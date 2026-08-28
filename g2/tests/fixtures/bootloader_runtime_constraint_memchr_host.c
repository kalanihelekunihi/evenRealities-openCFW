#include <stdint.h>
#include <stddef.h>

typedef void (*fixture_handler)(const char *, void *, uint32_t);
fixture_handler open_cfw_constraint_host_handler;
uint32_t open_cfw_constraint_fixture_handler_calls;
uint32_t open_cfw_constraint_fixture_default_calls;
uint32_t open_cfw_constraint_fixture_last_error;
const char *open_cfw_constraint_fixture_last_message;
void *open_cfw_constraint_fixture_last_pointer;

static void fixture_registered(const char *message, void *pointer, uint32_t error)
{
    ++open_cfw_constraint_fixture_handler_calls; open_cfw_constraint_fixture_last_message=message;
    open_cfw_constraint_fixture_last_pointer=pointer; open_cfw_constraint_fixture_last_error=error;
}
void open_cfw_constraint_host_default(const char *message)
{
    ++open_cfw_constraint_fixture_default_calls; open_cfw_constraint_fixture_last_message=message;
}
void open_cfw_constraint_fixture_reset(void)
{
    open_cfw_constraint_host_handler=0; open_cfw_constraint_fixture_handler_calls=0;
    open_cfw_constraint_fixture_default_calls=0; open_cfw_constraint_fixture_last_error=0;
    open_cfw_constraint_fixture_last_message=0; open_cfw_constraint_fixture_last_pointer=(void *)(uintptr_t)1;
}
void open_cfw_constraint_fixture_install_handler(void) { open_cfw_constraint_host_handler=fixture_registered; }
const char *open_cfw_constraint_fixture_message(void) { return open_cfw_constraint_fixture_last_message; }
uintptr_t open_cfw_constraint_fixture_pointer(void) { return (uintptr_t)open_cfw_constraint_fixture_last_pointer; }

#include "../../components/bootloader/core_overlay/runtime_constraint_memchr_422590.c"
