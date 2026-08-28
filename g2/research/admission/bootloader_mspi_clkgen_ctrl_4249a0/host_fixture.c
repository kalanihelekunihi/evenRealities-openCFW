/* SPDX-License-Identifier: BSD-3-Clause */
#include "runtime_bootloader_mspi_clkgen_ctrl_candidate.h"

typedef struct open_cfw_clkgen_fixture {
    uint32_t value;
    uint32_t token;
    uint32_t saved;
    uint32_t restored;
    uint32_t writes;
    uint32_t written[2];
    uint32_t delays;
    uint32_t delay_value;
} open_cfw_clkgen_fixture;
static open_cfw_clkgen_fixture fixture;
static uint32_t save(void *context) { open_cfw_clkgen_fixture *s=context; s->saved++; return s->token; }
static void restore(void *context, uint32_t token) { open_cfw_clkgen_fixture *s=context; s->restored=token; }
static uint32_t read_reg(void *context, uint32_t address) { (void)address; return ((open_cfw_clkgen_fixture *)context)->value; }
static void write_reg(void *context, uint32_t address, uint32_t value) { open_cfw_clkgen_fixture *s=context; (void)address; if(s->writes<2U)s->written[s->writes]=value; s->writes++; s->value=value; }
static void delay_us(void *context, uint32_t value) { open_cfw_clkgen_fixture *s=context; s->delays++; s->delay_value=value; }
void open_cfw_test_clkgen_reset(uint32_t value, uint32_t token) { fixture.value=value;fixture.token=token;fixture.saved=0;fixture.restored=0;fixture.writes=0;fixture.written[0]=0;fixture.written[1]=0;fixture.delays=0;fixture.delay_value=0; }
void open_cfw_test_clkgen_run(uint32_t module,uint32_t enable,uint32_t configure,uint32_t clock_select) { const open_cfw_mspi_clkgen_ports p={&fixture,save,restore,read_reg,write_reg,delay_us};open_cfw_bootloader_mspi_clkgen_ctrl_4249a0(module,enable,configure,clock_select,&p); }
uint32_t open_cfw_test_clkgen_value(uint32_t selector,uint32_t index) { if(selector==0)return fixture.value;if(selector==1)return fixture.saved;if(selector==2)return fixture.restored;if(selector==3)return fixture.writes;if(selector==4&&index<2)return fixture.written[index];if(selector==5)return fixture.delays;if(selector==6)return fixture.delay_value;return 0; }
