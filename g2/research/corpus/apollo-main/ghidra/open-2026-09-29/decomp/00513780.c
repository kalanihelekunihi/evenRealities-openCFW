
void FUN_00513780(undefined4 param_1,undefined2 param_2)

{
  undefined1 local_18;
  undefined1 local_17;
  undefined4 uStack_10;
  
  uStack_10 = param_1;
  FUN_0043c0e4(&local_18,2,0);
  local_17 = (undefined1)param_2;
  local_18 = (undefined1)((ushort)param_2 >> 8);
  hal_i2c_transfer_joined(2,0x45,&uStack_10,1,&local_18,2);
  return;
}

