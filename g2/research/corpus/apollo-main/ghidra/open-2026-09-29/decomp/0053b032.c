
void bq27427_i2c_write_reg(undefined4 param_1,undefined4 param_2,char param_3)

{
  if (param_3 == '\0') {
    hal_i2c_transfer_joined(7,0x55,&stack0xfffffff8,1,&stack0xfffffff9,2);
  }
  else {
    hal_i2c_transfer_joined(7,0x55,&stack0xfffffff8,1,&stack0xfffffff9,1);
  }
  return;
}

