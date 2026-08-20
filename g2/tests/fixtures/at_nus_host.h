#ifndef OPEN_CFW_AT_NUS_HOST_H
#define OPEN_CFW_AT_NUS_HOST_H

extern const char open_cfw_test_at_nus_response[];
extern const char *open_cfw_test_at_nus_written;
extern unsigned int open_cfw_test_at_nus_output_count;

void open_cfw_test_at_nus_reset(void);
void open_cfw_test_at_nus_output(const char *response);

#define OPEN_CFW_AT_NUS_RESPONSE_ADDRESS \
    ((unsigned long)open_cfw_test_at_nus_response)
#define OPEN_CFW_AT_NUS_OUTPUT(response) \
    open_cfw_test_at_nus_output((response))

#endif
