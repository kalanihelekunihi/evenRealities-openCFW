
undefined1 FUN_004c6fba(undefined4 *param_1,undefined4 param_2,undefined1 param_3)

{
  undefined1 uVar1;
  
  if (param_1[1] == 0) {
    uVar1 = 0xb;
  }
  else {
    if (*(int *)(param_1[1] + 4) == 0) {
      if (*(int *)(param_1[1] + 0x1c) == 0) {
        return 9;
      }
    }
    else if ((*(int *)(param_1[1] + 0x1c) == 0) || (*(int *)(param_1[1] + 0x20) == 0)) {
      return 9;
    }
    if (*(int *)(param_1[1] + 4) == 0) {
      uVar1 = (**(code **)(param_1[1] + 0x1c))(param_1[1],*param_1,param_2,param_3);
    }
    else {
      uVar1 = FUN_004c7364(param_1,param_2,param_3);
    }
  }
  return uVar1;
}

