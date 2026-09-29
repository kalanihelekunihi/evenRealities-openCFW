
uint bq27427_i2c_read_reg(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  undefined4 local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  uStack_14 = param_4;
  FUN_0043c0e4((int)&local_18 + 2,2,0,param_4,param_1,param_2);
  FUN_0043c0e4(&local_18,2,0);
  local_18._0_3_ = CONCAT12((char)param_1,(undefined2)local_18);
  hal_i2c_transfer_full(7,0x55,(int)&local_18 + 2,1,&local_18,1);
  uVar1 = local_18 & 0xff;
  if ((param_2 & 0xff) == 0) {
    local_18._0_3_ = CONCAT12((char)param_1 + '\x01',(undefined2)local_18);
    hal_i2c_transfer_full(7,0x55,(int)&local_18 + 2,1,(int)&local_18 + 1,1);
    uVar1 = local_18 & 0xffff;
  }
  return uVar1;
}

