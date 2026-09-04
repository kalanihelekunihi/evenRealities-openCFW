#include "eat_bond_connect_host.h"

const char open_cfw_test_eat_clean_response[] = "CLEANBOND+OK\r\n";
const char open_cfw_test_eat_keep_response[] = "BLE_KEEPCONNECT+OK\r\n";
const char *open_cfw_test_eat_written;
unsigned int open_cfw_test_eat_clean_calls;
unsigned int open_cfw_test_eat_keep_calls;
unsigned int open_cfw_test_eat_output_calls;
int open_cfw_test_eat_keep_argument;

void open_cfw_test_eat_reset(void)
{
    open_cfw_test_eat_written = 0;
    open_cfw_test_eat_clean_calls = 0;
    open_cfw_test_eat_keep_calls = 0;
    open_cfw_test_eat_output_calls = 0;
    open_cfw_test_eat_keep_argument = 0;
}

void open_cfw_test_eat_clean_bond(void)
{
    ++open_cfw_test_eat_clean_calls;
}

void open_cfw_test_eat_keep_connect(int enabled)
{
    ++open_cfw_test_eat_keep_calls;
    open_cfw_test_eat_keep_argument = enabled;
}

void open_cfw_test_eat_output(const char *response)
{
    ++open_cfw_test_eat_output_calls;
    open_cfw_test_eat_written = response;
}
