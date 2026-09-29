
undefined4 FUN_10002c38(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  uint *puVar6;
  uint uVar7;
  uint uVar8;
  
  if (*(int *)(param_1 + 0x1c) == 0) {
    *(undefined4 *)(param_1 + 0x1c) = 8;
  }
  if (*(int *)(param_1 + 0x20) == 0) {
    *(undefined4 *)(param_1 + 0x20) = 1;
  }
  puVar6 = *(uint **)(param_1 + 4);
  puVar6[1] = 0;
  uVar4 = 3;
  if (*(int *)(param_1 + 0x24) != 0) {
    uVar4 = 0x22;
  }
  puVar6[4] = uVar4;
  uVar7 = 0x6f;
  uVar4 = 0x6f;
  if (*(int *)(param_1 + 0x24) != 0) {
    uVar4 = 0x7f;
  }
  puVar6[2] = uVar4;
  if (*(int *)(param_1 + 0x10) != 0) {
    uVar4 = *(int *)(param_1 + 0x10) * 0x10;
    uVar8 = *(uint *)(param_1 + 0xc) / uVar4;
    *(uint *)(param_1 + 0x14) = uVar8;
    uVar1 = FUN_10007af8(*(uint *)(param_1 + 0xc) - uVar8 * uVar4);
    uVar3 = param_2;
    uVar2 = FUN_10007af8(uVar4);
    FUN_10007930(uVar1,param_2,uVar2,uVar3);
    FUN_10007730();
    FUN_100076c4();
    uVar3 = FUN_100073c8();
    *(undefined4 *)(param_1 + 0x18) = uVar3;
    puVar6[2] = 0;
    uVar4 = puVar6[3];
    puVar6[3] = uVar4 | 0x80;
    *puVar6 = uVar8 & 0xff;
    puVar6[1] = (uVar8 & 0x7fff) >> 8;
    puVar6[0x30] = (uint)*(byte *)(param_1 + 0x18);
    puVar6[3] = uVar4;
    if (*(int *)(param_1 + 0x24) != 0) {
      uVar7 = 0x7f;
    }
    puVar6[2] = uVar7;
  }
  puVar6[2] = 0;
  puVar6[3] = puVar6[3] & 0xffffffe0 | 3;
  uVar4 = 0x6f;
  if (*(int *)(param_1 + 0x24) != 0) {
    uVar4 = 0x7f;
  }
  puVar6[2] = uVar4;
  uVar4 = (puVar6[0x3d] & 0x7fffff) >> 0x10;
  if (uVar4 == 8) {
    *(undefined4 *)(param_1 + 0x30) = 0x80;
  }
  else if (uVar4 < 9) {
    if (uVar4 == 1) {
      *(undefined4 *)(param_1 + 0x30) = 0x10;
    }
    else if (uVar4 < 2) {
LAB_10002e08:
      *(undefined4 *)(param_1 + 0x30) = 0;
    }
    else if (uVar4 == 2) {
      *(undefined4 *)(param_1 + 0x30) = 0x20;
    }
    else {
      if (uVar4 != 4) goto LAB_10002e08;
      *(undefined4 *)(param_1 + 0x30) = 0x40;
    }
  }
  else if (uVar4 == 0x20) {
    *(undefined4 *)(param_1 + 0x30) = 0x200;
  }
  else if (uVar4 < 0x21) {
    if (uVar4 != 0x10) goto LAB_10002e08;
    *(undefined4 *)(param_1 + 0x30) = 0x100;
  }
  else if (uVar4 == 0x40) {
    *(undefined4 *)(param_1 + 0x30) = 0x400;
  }
  else {
    if (uVar4 != 0x80) goto LAB_10002e08;
    *(undefined4 *)(param_1 + 0x30) = 0x800;
  }
  uVar4 = puVar6[0x27];
  uVar7 = puVar6[0x28];
  if (uVar4 == 1) {
    uVar4 = *(uint *)(param_1 + 0x30);
    if ((uVar4 & 0x80000000) != 0) {
      uVar4 = uVar4 + 3;
    }
    *(int *)(param_1 + 0x38) = (int)uVar4 >> 2;
  }
  else if (uVar4 == 0) {
    *(undefined4 *)(param_1 + 0x38) = 1;
  }
  else if (uVar4 == 2) {
    *(int *)(param_1 + 0x38) = *(int *)(param_1 + 0x30) / 2;
  }
  else if (uVar4 == 3) {
    *(int *)(param_1 + 0x38) = *(int *)(param_1 + 0x30) + -2;
  }
  if (uVar7 == 1) {
    *(undefined4 *)(param_1 + 0x34) = 2;
  }
  else {
    iVar5 = 0;
    if (uVar7 != 0) {
      if (uVar7 != 2) {
        if (uVar7 == 3) {
          *(int *)(param_1 + 0x34) = *(int *)(param_1 + 0x30) / 2;
        }
        goto LAB_10002d0c;
      }
      uVar4 = *(uint *)(param_1 + 0x30);
      if ((uVar4 & 0x80000000) != 0) {
        uVar4 = uVar4 + 3;
      }
      iVar5 = (int)uVar4 >> 2;
    }
    *(int *)(param_1 + 0x34) = iVar5;
  }
LAB_10002d0c:
  *(undefined4 *)(param_1 + 0x2c) = 1;
  *(undefined4 *)(param_1 + 0x68) = 0xffffffff;
  *(undefined4 *)(param_1 + 0x7c) = 0xffffffff;
  FUN_100030e8(*(undefined4 *)(param_1 + 0x3c),PTR_LAB_10002e24,param_1);
  return 0;
}

