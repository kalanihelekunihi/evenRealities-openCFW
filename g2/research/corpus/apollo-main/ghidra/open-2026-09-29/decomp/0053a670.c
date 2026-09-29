
longlong bq25180_write_register(void)

{
  undefined1 *puVar1;
  
  puVar1 = &stack0xfffffff9;
  hal_i2c_transfer_joined(7,0x6a,&stack0xfffffff8,1,puVar1,1);
  return ZEXT48(puVar1) << 0x20;
}

