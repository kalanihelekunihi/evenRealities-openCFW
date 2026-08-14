#ifndef OPENR1_ADVERTISING_H
#define OPENR1_ADVERTISING_H

#include <stdbool.h>
#include <stdint.h>

uint32_t openr1_advertising_initialize(bool factory_mode,
                                        const uint8_t product_serial[15],
                                        bool serial_provisioned);
uint32_t openr1_advertising_start(void);
uint32_t openr1_advertising_stop(void);
/* Resynchronize the local advertiser state after the SoftDevice stops the
   advertiser for an established connection (no module event reports it). */
void openr1_advertising_connection_established(bool peripheral_role);
/* Recovered R1 role policy: advertise fast while either the phone or the
   glasses role is unoccupied; stop once both roles are occupied. */
uint32_t openr1_advertising_set_role_occupancy(bool phone_occupied,
                                               bool glasses_occupied);
uint32_t openr1_advertising_last_error(void);

#endif
