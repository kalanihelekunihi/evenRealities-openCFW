ENTRY(Cy_SCB_I2C_SlaveInterrupt)
SECTIONS {
 .assembly 0x4480 : { *assembly.o(.text) }
 .read_helper 0x9218 : { *(.text.Cy_SCB_ReadArrayNoCheck) }
 .read 0x9250 : { *(.text.Cy_SCB_ReadArray) }
 .write_helper 0x926E : { *(.text.Cy_SCB_WriteArrayNoCheck) }
 .write 0x92A6 : { *(.text.Cy_SCB_WriteArray) }
 .default_helper 0x92D6 : { *(.text.Cy_SCB_WriteDefaultArrayNoCheck) }
 .default 0x92E6 : { *(.text.Cy_SCB_WriteDefaultArray) }
 .rx_level 0x9316 : { *(.text.Cy_SCB_SetRxFifoLevel) }
 .hs 0x9344 : { *(.text.SlaveHandleHsMode) }
 .stop 0x93C4 : { *(.text.SlaveHandleStop) }
 .ack 0x9510 : { *(.text.SlaveHandleAck) }
 .address 0x95B8 : { *(.text.SlaveHandleAddress) }
 .receive 0x9748 : { *(.text.SlaveHandleDataReceive) }
 .transmit 0x97FC : { *(.text.SlaveHandleDataTransmit) }
 .interrupt 0x9B0C : { *(.text.Cy_SCB_I2C_SlaveInterrupt) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
