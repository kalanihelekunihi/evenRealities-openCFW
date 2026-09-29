
undefined8 FUN_004ce914(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  *(int *)(param_1 + 0x68) = param_2;
  *(undefined4 *)(param_1 + 0x6c) = *(undefined4 *)(param_2 + 0x20);
  if (*(int *)(*(int *)(param_1 + 0x68) + 4) == 0) {
    FUN_004d09b4(DAT_004cf478,DAT_004cedf4,0x1078);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 8) == 0) {
    FUN_004d09b4(DAT_004cf47c,DAT_004cedf4,0x107a);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0xc) == 0) {
    FUN_004d09b4(DAT_004cf480,DAT_004cedf4,0x107b);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0x10) == 0) {
    FUN_004d09b4(DAT_004cf484,DAT_004cedf4,0x107c);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0x14) == 0) {
    FUN_004d09b4(DAT_004cf488,DAT_004cedf4,0x1081);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0x18) == 0) {
    FUN_004d09b4(DAT_004cf48c,DAT_004cedf4,0x1082);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0x28) == 0) {
    FUN_004d09b4(DAT_004cf490,DAT_004cedf4,0x1083);
  }
  uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x28);
  uVar4 = *(uint *)(*(int *)(param_1 + 0x68) + 0x14);
  if (uVar1 != uVar4 * (uVar1 / uVar4)) {
    FUN_004d09b4(DAT_004cf554,DAT_004cedf4,0x1087);
  }
  uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x28);
  uVar4 = *(uint *)(*(int *)(param_1 + 0x68) + 0x18);
  if (uVar1 != uVar4 * (uVar1 / uVar4)) {
    FUN_004d09b4(DAT_004cf558,DAT_004cedf4,0x1088);
  }
  uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x1c);
  uVar4 = *(uint *)(*(int *)(param_1 + 0x68) + 0x28);
  if (uVar1 != uVar4 * (uVar1 / uVar4)) {
    FUN_004d09b4(DAT_004cf55c,DAT_004cedf4,0x1089);
  }
  if (*(uint *)(*(int *)(param_1 + 0x68) + 0x1c) < 0x80) {
    FUN_004d09b4(DAT_004cf560,DAT_004cedf4,0x108c);
  }
  iVar2 = lfs_npw2(0xffffffff / (*(int *)(*(int *)(param_1 + 0x68) + 0x1c) - 8U));
  if (*(uint *)(*(int *)(param_1 + 0x68) + 0x1c) < (uint)(iVar2 << 2)) {
    FUN_004d09b4(DAT_004cf5e4,DAT_004cedf4,0x1090);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0x24) == 0) {
    FUN_004d09b4(DAT_004cf5e8,DAT_004cedf4,0x1098);
  }
  if ((*(int *)(*(int *)(param_1 + 0x68) + 0x30) != 0) &&
     (*(uint *)(*(int *)(param_1 + 0x68) + 0x30) < *(uint *)(*(int *)(param_1 + 0x68) + 0x1c) >> 1))
  {
    FUN_004d09b4(DAT_004cf63c,DAT_004cedf4,0x109f);
  }
  if ((*(int *)(*(int *)(param_1 + 0x68) + 0x30) != -1) &&
     (*(uint *)(*(int *)(param_1 + 0x68) + 0x1c) < *(uint *)(*(int *)(param_1 + 0x68) + 0x30))) {
    FUN_004d09b4(DAT_004cf640,DAT_004cedf4,0x10a1);
  }
  if ((*(int *)(*(int *)(param_1 + 0x68) + 0x4c) != 0) &&
     (uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x4c),
     uVar4 = *(uint *)(*(int *)(param_1 + 0x68) + 0x14), uVar1 != uVar4 * (uVar1 / uVar4))) {
    FUN_004d09b4(DAT_004cf644,DAT_004cedf4,0x10a6);
  }
  if ((*(int *)(*(int *)(param_1 + 0x68) + 0x4c) != 0) &&
     (uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x4c),
     uVar4 = *(uint *)(*(int *)(param_1 + 0x68) + 0x18), uVar1 != uVar4 * (uVar1 / uVar4))) {
    FUN_004d09b4(DAT_004cf6dc,DAT_004cedf4,0x10a8);
  }
  if ((*(int *)(*(int *)(param_1 + 0x68) + 0x4c) != 0) &&
     (uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x1c),
     uVar4 = *(uint *)(*(int *)(param_1 + 0x68) + 0x4c), uVar1 != uVar4 * (uVar1 / uVar4))) {
    FUN_004d09b4(DAT_004cf6e0,DAT_004cedf4,0x10aa);
  }
  if (*(int *)(*(int *)(param_1 + 0x68) + 0x34) == 0) {
    uVar3 = FUN_004ca80a(*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x28));
    *(undefined4 *)(param_1 + 0xc) = uVar3;
    if (*(int *)(param_1 + 0xc) != 0) goto LAB_004cebac;
LAB_004ced1c:
    uVar3 = 0xfffffff4;
    FUN_004cedf8(param_1);
  }
  else {
    *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x34);
LAB_004cebac:
    if (*(int *)(*(int *)(param_1 + 0x68) + 0x38) == 0) {
      uVar3 = FUN_004ca80a(*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x28));
      *(undefined4 *)(param_1 + 0x1c) = uVar3;
      if (*(int *)(param_1 + 0x1c) == 0) goto LAB_004ced1c;
    }
    else {
      *(undefined4 *)(param_1 + 0x1c) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x38);
    }
    FUN_004ca822(param_1,param_1);
    FUN_004ca822(param_1,param_1 + 0x10);
    if (*(int *)(*(int *)(param_1 + 0x68) + 0x2c) == 0) {
      FUN_004d09b4(DAT_004cf6e4,DAT_004cedf4,0x10c8);
    }
    if (*(int *)(*(int *)(param_1 + 0x68) + 0x3c) == 0) {
      uVar3 = FUN_004ca80a(*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x2c));
      *(undefined4 *)(param_1 + 100) = uVar3;
      if (*(int *)(param_1 + 100) == 0) goto LAB_004ced1c;
    }
    else {
      *(undefined4 *)(param_1 + 100) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x3c);
    }
    if (0xff < *(uint *)(*(int *)(param_1 + 0x68) + 0x40)) {
      FUN_004d09b4(DAT_004cf794,DAT_004cedf4,0x10d4);
    }
    *(undefined4 *)(param_1 + 0x70) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x40);
    if (*(int *)(param_1 + 0x70) == 0) {
      *(undefined4 *)(param_1 + 0x70) = 0xff;
    }
    if (0x7fffffff < *(uint *)(*(int *)(param_1 + 0x68) + 0x44)) {
      FUN_004d09b4(DAT_004cf798,DAT_004cedf4,0x10da);
    }
    *(undefined4 *)(param_1 + 0x74) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x44);
    if (*(int *)(param_1 + 0x74) == 0) {
      *(undefined4 *)(param_1 + 0x74) = 0x7fffffff;
    }
    if (0x3fe < *(uint *)(*(int *)(param_1 + 0x68) + 0x48)) {
      FUN_004d09b4(DAT_004cf79c,DAT_004cedf4,0x10e0);
    }
    *(undefined4 *)(param_1 + 0x78) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x48);
    if (*(int *)(param_1 + 0x78) == 0) {
      *(undefined4 *)(param_1 + 0x78) = 0x3fe;
    }
    if (*(uint *)(*(int *)(param_1 + 0x68) + 0x1c) < *(uint *)(*(int *)(param_1 + 0x68) + 0x4c)) {
      FUN_004d09b4(DAT_004cf7a0,DAT_004cedf4,0x10e6);
    }
    if ((*(int *)(*(int *)(param_1 + 0x68) + 0x50) != -1) &&
       (*(uint *)(*(int *)(param_1 + 0x68) + 0x28) < *(uint *)(*(int *)(param_1 + 0x68) + 0x50))) {
      FUN_004d09b4(DAT_004cf7a4,DAT_004cedf4,0x10e9);
    }
    if ((*(int *)(*(int *)(param_1 + 0x68) + 0x50) != -1) &&
       (*(uint *)(param_1 + 0x78) < *(uint *)(*(int *)(param_1 + 0x68) + 0x50))) {
      FUN_004d09b4(DAT_004cf7a8,DAT_004cedf4,0x10eb);
    }
    if (*(int *)(*(int *)(param_1 + 0x68) + 0x50) != -1) {
      if (*(int *)(*(int *)(param_1 + 0x68) + 0x4c) == 0) {
        uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x1c);
      }
      else {
        uVar1 = *(uint *)(*(int *)(param_1 + 0x68) + 0x4c);
      }
      if (uVar1 >> 3 < *(uint *)(*(int *)(param_1 + 0x68) + 0x50)) {
        FUN_004d09b4(DAT_004cf9d4,DAT_004cedf4,0x10ef);
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

