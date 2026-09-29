
bool FUN_00529ea2(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  undefined4 local_30 [2];
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 uStack_14;
  
  bVar1 = *(int *)(param_1 + 0x10) != 0;
  uStack_14 = param_4;
  if (bVar1) {
    FUN_00529b2c(local_30,0x1c);
    local_24 = 0;
    local_28 = param_2;
    local_20 = param_3;
    (**(code **)(param_1 + 0x10))(local_30);
  }
  else {
    local_30[0] = DAT_0052a238;
    FUN_0044d25c(3,DAT_0052a20c,0xe3,DAT_0052a23c);
  }
  return bVar1;
}

