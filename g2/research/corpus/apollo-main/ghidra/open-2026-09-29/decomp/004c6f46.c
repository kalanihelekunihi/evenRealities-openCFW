
undefined8
FUN_004c6f46(undefined4 *param_1,undefined4 *param_2,undefined4 param_3,undefined4 *param_4)

{
  byte bVar1;
  uint uVar2;
  undefined4 *local_18;
  undefined4 local_14;
  undefined4 *puStack_10;
  
  local_18 = &local_14;
  if (param_4 != (undefined4 *)0x0) {
    *param_4 = 0;
  }
  if (param_1[1] == 0) {
    uVar2 = 0xb;
    local_18 = param_2;
  }
  else {
    if (*(int *)(param_1[1] + 4) == 0) {
      if (*(int *)(param_1[1] + 0x14) == 0) {
        uVar2 = 9;
        local_18 = param_2;
        goto LAB_004c6fb8;
      }
    }
    else if ((*(int *)(param_1[1] + 0x14) == 0) || (*(int *)(param_1[1] + 0x1c) == 0)) {
      uVar2 = 9;
      local_18 = param_2;
      goto LAB_004c6fb8;
    }
    local_14 = 0;
    puStack_10 = param_4;
    if (*(int *)(param_1[1] + 4) == 0) {
      bVar1 = (**(code **)(param_1[1] + 0x14))(param_1[1],*param_1,param_2,param_3);
    }
    else {
      bVar1 = FUN_004c713c(param_1,param_2,param_3,local_18);
      local_18 = param_2;
    }
    if (param_4 != (undefined4 *)0x0) {
      *param_4 = local_14;
    }
    uVar2 = (uint)bVar1;
  }
LAB_004c6fb8:
  return CONCAT44(local_18,uVar2);
}

