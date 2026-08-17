#ifndef OPENR1_SOFTWARE_TWI_ZEPHYR_H
#define OPENR1_SOFTWARE_TWI_ZEPHYR_H

#include "software_twi/software_twi.h"

int openr1_software_twi_zephyr_initialize(void);
int openr1_software_twi_zephyr_open(software_twi_bus_id bus);
int openr1_software_twi_zephyr_read(
    software_twi_bus_id bus, const software_twi_read_request *request);
int openr1_software_twi_zephyr_write(
    software_twi_bus_id bus, const software_twi_write_request *request);
void openr1_software_twi_zephyr_close(software_twi_bus_id bus);

#endif
