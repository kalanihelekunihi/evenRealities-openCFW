
undefined8 FUN_00413ff8(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  *(int *)(param_1 + 0x68) = param_2;
  *(undefined4 *)(param_1 + 0x6c) = *(undefined4 *)(param_2 + 0x20);
  if (*(int *)(*(int *)(param_1 + 0x68) + 4) == 0) {
    FUN_00415734(DAT_00414b48,DAT_004144d8,0x1078);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 8) == 0) {
    FUN_00415734(DAT_00414b4c,DAT_004144d8,0x107a);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0xc) == 0) {
    FUN_00415734(DAT_00414b50,DAT_004144d8,0x107b);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0x10) == 0) {
    FUN_00415734(DAT_00414b54,DAT_004144d8,0x107c);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0x14) == 0) {
    FUN_00415734(DAT_00414b58,DAT_004144d8,0x1081);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0x18) == 0) {
    FUN_00415734(DAT_00414b5c,DAT_004144d8,0x1082);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0x28) == 0) {
    FUN_00415734(DAT_00414b60,DAT_004144d8,0x1083);
  }
  uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x28);
  uVar4 = *(uint *)(*(int *)(param_1 + 0x68) + 0x14);
  if (uVar1 != uVar4 * (uVar1 / uVar4)) {
    FUN_00415734(DAT_00414c24,DAT_004144d8,0x1087);
  }
  uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x28);
  uVar4 = *(uint *)(*(int *)(param_1 + 0x68) + 0x18);
  if (uVar1 != uVar4 * (uVar1 / uVar4)) {
    FUN_00415734(DAT_00414c28,DAT_004144d8,0x1088);
  }
  uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x1c);
  uVar4 = *(uint *)(*(int *)(param_1 + 0x68) + 0x28);
  if (uVar1 != uVar4 * (uVar1 / uVar4)) {
    FUN_00415734(DAT_00414c2c,DAT_004144d8,0x1089);
  }
  if (*(uint *)(*(int *)(param_1 + 0x68) + 0x1c) < 0x80) {
    FUN_00415734(DAT_00414c30,DAT_004144d8,0x108c);
  }
  iVar2 = lfs_npw2(0xffffffff / (*(int *)(*(int *)(param_1 + 0x68) + 0x1c) - 8U));
  if (*(uint *)(*(int *)(param_1 + 0x68) + 0x1c) < (uint)(iVar2 << 2)) {
    FUN_00415734(DAT_00414cb4,DAT_004144d8,0x1090);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0x24) == 0) {
    FUN_00415734(DAT_00414cb8,DAT_004144d8,0x1098);
  }
  if ((*(int *)(*(int *)(param_1 + 0x68) + 0x30) != 0) &&
     (*(uint *)(*(int *)(param_1 + 0x68) + 0x30) < *(uint *)(*(int *)(param_1 + 0x68) + 0x1c) >> 1))
  {
    FUN_00415734(DAT_00414d0c,DAT_004144d8,0x109f);
  }
  if ((*(int *)(*(int *)(param_1 + 0x68) + 0x30) != -1) &&
     (*(uint *)(*(int *)(param_1 + 0x68) + 0x1c) < *(uint *)(*(int *)(param_1 + 0x68) + 0x30))) {
    FUN_00415734(DAT_00414d10,DAT_004144d8,0x10a1);
  }
  if ((*(int *)(*(int *)(param_1 + 0x68) + 0x4c) != 0) &&
     (uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x4c),
     uVar4 = *(uint *)(*(int *)(param_1 + 0x68) + 0x14), uVar1 != uVar4 * (uVar1 / uVar4))) {
    FUN_00415734(DAT_00414d14,DAT_004144d8,0x10a6);
  }
  if ((*(int *)(*(int *)(param_1 + 0x68) + 0x4c) != 0) &&
     (uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x4c),
     uVar4 = *(uint *)(*(int *)(param_1 + 0x68) + 0x18), uVar1 != uVar4 * (uVar1 / uVar4))) {
    FUN_00415734(DAT_00414dac,DAT_004144d8,0x10a8);
  }
  if ((*(int *)(*(int *)(param_1 + 0x68) + 0x4c) != 0) &&
     (uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x1c),
     uVar4 = *(uint *)(*(int *)(param_1 + 0x68) + 0x4c), uVar1 != uVar4 * (uVar1 / uVar4))) {
    FUN_00415734(DAT_00414db0,DAT_004144d8,0x10aa);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0x34) == 0) {
    uVar3 = FUN_00410512(*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x28));
    *(undefined4 *)(param_1 + 0xc) = uVar3;
    if (*(int *)(param_1 + 0xc) != 0) goto LAB_00414290;
LAB_00414400:
    uVar3 = 0xfffffff4;
    FUN_004144dc(param_1);
  }
  else {
    *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x34);
LAB_00414290:
    if (*(int *)(*(int *)(param_1 + 0x68) + 0x38) == 0) {
      uVar3 = FUN_00410512(*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x28));
      *(undefined4 *)(param_1 + 0x1c) = uVar3;
      if (*(int *)(param_1 + 0x1c) == 0) goto LAB_00414400;
    }
    else {
      *(undefined4 *)(param_1 + 0x1c) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x38);
    }
    FUN_0041052a(param_1,param_1);
    FUN_0041052a(param_1,param_1 + 0x10);
    if (*(int *)(*(int *)(param_1 + 0x68) + 0x2c) == 0) {
      FUN_00415734(DAT_00414db4,DAT_004144d8,0x10c8);
    }
    if (*(int *)(*(int *)(param_1 + 0x68) + 0x3c) == 0) {
      uVar3 = FUN_00410512(*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x2c));
      *(undefined4 *)(param_1 + 100) = uVar3;
      if (*(int *)(param_1 + 100) == 0) goto LAB_00414400;
    }
    else {
      *(undefined4 *)(param_1 + 100) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x3c);
    }
    if (0xff < *(uint *)(*(int *)(param_1 + 0x68) + 0x40)) {
      FUN_00415734(DAT_00414e64,DAT_004144d8,0x10d4);
    }
    *(undefined4 *)(param_1 + 0x70) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x40);
    if (*(int *)(param_1 + 0x70) == 0) {
      *(undefined4 *)(param_1 + 0x70) = 0xff;
    }
    if (0x7fffffff < *(uint *)(*(int *)(param_1 + 0x68) + 0x44)) {
      FUN_00415734(DAT_00414e68,DAT_004144d8,0x10da);
    }
    *(undefined4 *)(param_1 + 0x74) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x44);
    if (*(int *)(param_1 + 0x74) == 0) {
      *(undefined4 *)(param_1 + 0x74) = 0x7fffffff;
    }
    if (0x3fe < *(uint *)(*(int *)(param_1 + 0x68) + 0x48)) {
      FUN_00415734(DAT_00414e6c,DAT_004144d8,0x10e0);
    }
    *(undefined4 *)(param_1 + 0x78) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x48);
    if (*(int *)(param_1 + 0x78) == 0) {
      *(undefined4 *)(param_1 + 0x78) = 0x3fe;
    }
    if (*(uint *)(*(int *)(param_1 + 0x68) + 0x1c) < *(uint *)(*(int *)(param_1 + 0x68) + 0x4c)) {
      FUN_00415734(DAT_00414e70,DAT_004144d8,0x10e6);
    }
    if ((*(int *)(*(int *)(param_1 + 0x68) + 0x50) != -1) &&
       (*(uint *)(*(int *)(param_1 + 0x68) + 0x28) < *(uint *)(*(int *)(param_1 + 0x68) + 0x50))) {
      FUN_00415734(DAT_00414e74,DAT_004144d8,0x10e9);
    }
    if ((*(int *)(*(int *)(param_1 + 0x68) + 0x50) != -1) &&
       (*(uint *)(param_1 + 0x78) < *(uint *)(*(int *)(param_1 + 0x68) + 0x50))) {
      FUN_00415734(DAT_00414e78,DAT_004144d8,0x10eb);
    }
    if (*(int *)(*(int *)(param_1 + 0x68) + 0x50) != -1) {
      if (*(int *)(*(int *)(param_1 + 0x68) + 0x4c) == 0) {
        uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x1c);
      }
      else {
        uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x4c);
      }
      if (uVar1 >> 3 < *(uint *)(*(int *)(param_1 + 0x68) + 0x50)) {
        FUN_00415734(DAT_004150a4,DAT_004144d8,0x10ef);
      }
    }
    *(undefined4 *)(param_1 + 0x7c) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x50);
    if (*(int *)(param_1 + 0x7c) == -1) {
      *(undefined4 *)(param_1 + 0x7c) = 0;
    }
    else if (*(int *)(param_1 + 0x7c) == 0) {
      if (*(int *)(*(int *)(param_1 + 0x68) + 0x4c) == 0) {
        uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x1c);
      }
      else {
        uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x4c);
      }
      uVar3 = lfs_min(*(undefined4 *)(param_1 + 0x78),uVar1 >> 3);
      uVar3 = lfs_min(*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x28),uVar3);
      *(undefined4 *)(param_1 + 0x7c) = uVar3;
    }
    *(undefined4 *)(param_1 + 0x20) = 0xffffffff;
    *(undefined4 *)(param_1 + 0x24) = 0xffffffff;
    *(undefined4 *)(param_1 + 0x28) = 0;
    *(undefined4 *)(param_1 + 0x2c) = 0;
    *(undefined4 *)(param_1 + 0x3c) = 0;
    *(undefined4 *)(param_1 + 0x40) = 0;
    *(undefined4 *)(param_1 + 0x44) = 0;
    *(undefined4 *)(param_1 + 0x30) = 0;
    *(undefined4 *)(param_1 + 0x34) = 0;
    *(undefined4 *)(param_1 + 0x38) = 0;
    *(undefined4 *)(param_1 + 0x48) = 0;
    *(undefined4 *)(param_1 + 0x4c) = 0;
    *(undefined4 *)(param_1 + 0x50) = 0;
    uVar3 = 0;
  }
  return CONCAT44(param_4,uVar3);
}

