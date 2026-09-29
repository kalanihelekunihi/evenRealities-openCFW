
void bq27427_i2c_read_block(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  hal_i2c_transfer_full(7,0x55,&stack0xfffffff8,1,param_2,param_3);
  return;
}

