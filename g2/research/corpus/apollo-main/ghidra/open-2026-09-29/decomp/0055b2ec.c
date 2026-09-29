
void FUN_0055b2ec(undefined4 param_1,undefined4 param_2,undefined2 param_3)

{
  undefined4 uStack_8;
  
  uStack_8 = param_1;
  hal_i2c_transfer_joined(5,0xc,&uStack_8,1,param_2,param_3);
  return;
}

