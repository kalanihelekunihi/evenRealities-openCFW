
undefined8 AppAdvSetData(undefined1 param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_18;
  undefined4 local_14;
  
  iVar1 = appSlaveAdvMode();
  local_18 = param_3;
  local_14 = param_4;
  if (iVar1 != 0) {
    if (0x1f < param_2) {
      param_2 = 0x1f;
    }
    local_14 = 0x1f;
    local_18 = 0x1f;
    FUN_004b4240(0,param_1,param_2,param_3);
  }
  return CONCAT44(local_14,local_18);
}

