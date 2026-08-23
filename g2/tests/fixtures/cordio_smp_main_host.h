#ifndef OPEN_CFW_CORDIO_SMP_MAIN_HOST_H
#define OPEN_CFW_CORDIO_SMP_MAIN_HOST_H

#include <stdint.h>

struct open_cfw_smp_main_control_block;

extern struct open_cfw_smp_main_control_block open_cfw_test_smp_main_control;
extern uint8_t open_cfw_test_smp_main_security_queue;

#define OPEN_CFW_SMP_MAIN_CONTROL_BLOCK open_cfw_test_smp_main_control
#define OPEN_CFW_SMP_MAIN_SECURITY_QUEUE \
    ((void *)&open_cfw_test_smp_main_security_queue)

#endif
