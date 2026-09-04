#ifndef OPEN_CFW_EAT_BOND_CONNECT_HOST_H
#define OPEN_CFW_EAT_BOND_CONNECT_HOST_H

extern const char open_cfw_test_eat_clean_response[];
extern const char open_cfw_test_eat_keep_response[];
extern const char *open_cfw_test_eat_written;
extern unsigned int open_cfw_test_eat_clean_calls;
extern unsigned int open_cfw_test_eat_keep_calls;
extern unsigned int open_cfw_test_eat_output_calls;
extern int open_cfw_test_eat_keep_argument;

void open_cfw_test_eat_reset(void);
void open_cfw_test_eat_clean_bond(void);
void open_cfw_test_eat_keep_connect(int enabled);
void open_cfw_test_eat_output(const char *response);

#define OPEN_CFW_EAT_CLEAN_BOND_RESPONSE_ADDRESS \
    ((unsigned long)open_cfw_test_eat_clean_response)
#define OPEN_CFW_EAT_KEEP_CONNECT_RESPONSE_ADDRESS \
    ((unsigned long)open_cfw_test_eat_keep_response)
#define OPEN_CFW_EAT_CLEAN_BOND() open_cfw_test_eat_clean_bond()
#define OPEN_CFW_EAT_KEEP_CONNECT(enabled) \
    open_cfw_test_eat_keep_connect((enabled))
#define OPEN_CFW_EAT_OUTPUT(response) open_cfw_test_eat_output((response))

#endif
