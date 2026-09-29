
ulonglong bq25180_read_register(void)

{
  ushort unaff_r7;
  undefined1 *puVar1;
  
  puVar1 = &stack0xfffffff8;
  hal_i2c_transfer_full(7,0x6a,&stack0xfffffffa,1,puVar1,1);
  return CONCAT44(puVar1,(uint)unaff_r7) & 0xffffffff000000ff;
}

