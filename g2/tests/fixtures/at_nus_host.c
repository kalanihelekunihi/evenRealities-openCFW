#include "at_nus_host.h"

const char open_cfw_test_at_nus_response[] = "NUS+OK\r\n";
const char *open_cfw_test_at_nus_written;
unsigned int open_cfw_test_at_nus_output_count;

void open_cfw_test_at_nus_output(const char *response)
{
    open_cfw_test_at_nus_written = response;
    ++open_cfw_test_at_nus_output_count;
}

void open_cfw_test_at_nus_reset(void)
{
    open_cfw_test_at_nus_written = 0;
    open_cfw_test_at_nus_output_count = 0;
}
