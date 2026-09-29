
undefined8
FUN_004c6ee0(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  
  if (param_1[1] == 0) {
    uVar1 = 0xb;
  }
  else if (*(int *)(param_1[1] + 0x10) == 0) {
    uVar1 = 9;
  }
  else {
    uVar1 = (**(code **)(param_1[1] + 0x10))(param_1[1],*param_1);
    if ((*(int *)(param_1[1] + 4) != 0) && (param_1[2] != 0)) {
      if ((*(int *)(param_1[1] + 4) != -1) && (*(int *)(param_1[2] + 0xc) != 0)) {
        FUN_0044f758(*(undefined4 *)(param_1[2] + 0xc));
      }
      FUN_0044f758(param_1[2]);
    }
    *param_1 = 0;
    param_1[1] = 0;
    param_1[2] = 0;
    uVar1 = uVar1 & 0xff;
  }
  return CONCAT44(param_4,uVar1);
}

