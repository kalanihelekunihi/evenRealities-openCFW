
void FUN_00450910(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if ((((*(byte *)(param_1 + 0x5c) & 3) >> 1 == 0) && (*(int *)(param_1 + 0x44) != 0)) &&
     (*(int *)(param_1 + 0x44) != -1)) {
    *(int *)(param_1 + 0x44) = *(int *)(param_1 + 0x44) + -1;
  }
  if ((*(int *)(param_1 + 0x44) == 0) &&
     ((*(int *)(param_1 + 0x3c) == 0 || ((*(byte *)(param_1 + 0x5c) & 3) >> 1 != 0)))) {
    FUN_00482c0e(DAT_00450b48,param_1);
    FUN_004509da();
    if (*(int *)(param_1 + 0x10) != 0) {
      (**(code **)(param_1 + 0x10))(param_1);
    }
    if (*(int *)(param_1 + 0x14) != 0) {
      (**(code **)(param_1 + 0x14))(param_1);
    }
    FUN_0044f758(param_1);
  }
  else {
    iVar2 = 0;
    if (*(int *)(param_1 + 0x30) < *(int *)(param_1 + 0x34)) {
      iVar2 = *(int *)(param_1 + 0x34) - *(int *)(param_1 + 0x30);
    }
    *(int *)(param_1 + 0x34) = iVar2 - *(int *)(param_1 + 0x40);
    if (*(int *)(param_1 + 0x3c) != 0) {
      if ((*(byte *)(param_1 + 0x5c) & 3) >> 1 == 0) {
        *(int *)(param_1 + 0x34) = -*(int *)(param_1 + 0x38);
      }
      *(byte *)(param_1 + 0x5c) =
           *(byte *)(param_1 + 0x5c) & 0xfd | (*(byte *)(param_1 + 0x5c) >> 1 & 1 ^ 1) << 1;
      uVar1 = *(undefined4 *)(param_1 + 0x24);
      *(undefined4 *)(param_1 + 0x24) = *(undefined4 *)(param_1 + 0x2c);
      *(undefined4 *)(param_1 + 0x2c) = uVar1;
      uVar1 = *(undefined4 *)(param_1 + 0x30);
      *(undefined4 *)(param_1 + 0x30) = *(undefined4 *)(param_1 + 0x3c);
      *(undefined4 *)(param_1 + 0x3c) = uVar1;
    }
  }
  return;
}

