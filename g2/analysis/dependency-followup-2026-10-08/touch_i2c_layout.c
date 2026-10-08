/* Public PDL ABI measurement only; no device operations. */
#include <stddef.h>
#include "cy_scb_i2c.h"
const unsigned int touch_i2c_layout[] = {
 sizeof(cy_en_scb_i2c_mode_t), sizeof(cy_stc_scb_i2c_config_t),
 offsetof(cy_stc_scb_i2c_config_t,useRxFifo), offsetof(cy_stc_scb_i2c_config_t,useTxFifo),
 offsetof(cy_stc_scb_i2c_config_t,slaveAddress), offsetof(cy_stc_scb_i2c_config_t,slaveAddressMask),
 offsetof(cy_stc_scb_i2c_config_t,acceptAddrInFifo), offsetof(cy_stc_scb_i2c_config_t,ackGeneralAddr),
 offsetof(cy_stc_scb_i2c_config_t,hsEnable), offsetof(cy_stc_scb_i2c_config_t,enableWakeFromSleep),
 offsetof(cy_stc_scb_i2c_config_t,enableDigitalFilter), offsetof(cy_stc_scb_i2c_config_t,lowPhaseDutyCycle),
 offsetof(cy_stc_scb_i2c_config_t,highPhaseDutyCycle), offsetof(cy_stc_scb_i2c_config_t,delayInFifoAddress),
 sizeof(cy_stc_scb_i2c_context_t), offsetof(cy_stc_scb_i2c_context_t,state),
 offsetof(cy_stc_scb_i2c_context_t,masterStatus), offsetof(cy_stc_scb_i2c_context_t,slaveStatus),
 offsetof(cy_stc_scb_i2c_context_t,cbEvents), offsetof(cy_stc_scb_i2c_context_t,cbAddr),
 offsetof(cy_stc_scb_i2c_context_t,cbHsMode), offsetof(cy_stc_scb_i2c_context_t,delayInFifoAddress)
};
