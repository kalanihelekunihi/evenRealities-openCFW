
undefined4 FUN_100043a4(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  uint *puVar7;
  uint uVar8;
  uint uVar9;
  
  if (*(int *)(param_1 + 0x1c) == 0) {
    *(undefined4 *)(param_1 + 0x1c) = 8;
  }
  if (*(int *)(param_1 + 0x20) == 0) {
    *(undefined4 *)(param_1 + 0x20) = 1;
  }
  puVar7 = *(uint **)(param_1 + 4);
  puVar7[1] = 0;
  uVar4 = 3;
  if (*(int *)(param_1 + 0x24) != 0) {
    uVar4 = 0x22;
  }
  puVar7[4] = uVar4;
  uVar8 = 0x6f;
  uVar4 = 0x6f;
  if (*(int *)(param_1 + 0x24) != 0) {
    uVar4 = 0x7f;
  }
  puVar7[2] = uVar4;
  if (*(int *)(param_1 + 0x10) != 0) {
    uVar4 = *(int *)(param_1 + 0x10) * 0x10;
    uVar9 = *(uint *)(param_1 + 0xc) / uVar4;
    *(uint *)(param_1 + 0x14) = uVar9;
    uVar1 = FUN_100123cc(*(uint *)(param_1 + 0xc) - uVar9 * uVar4);
    uVar6 = param_2;
    uVar2 = FUN_100123cc(uVar4);
    FUN_10012050(uVar1,param_2,uVar2,uVar6);
    FUN_10011e50();
    FUN_10011de4();
    uVar6 = FUN_10011464();
    *(undefined4 *)(param_1 + 0x18) = uVar6;
    puVar7[2] = 0;
    uVar4 = puVar7[3];
    puVar7[3] = uVar4 | 0x80;
    *puVar7 = uVar9 & 0xff;
    puVar7[1] = (uVar9 & 0x7fff) >> 8;
    puVar7[0x30] = (uint)*(byte *)(param_1 + 0x18);
    puVar7[3] = uVar4;
    if (*(int *)(param_1 + 0x24) != 0) {
      uVar8 = 0x7f;
    }
    puVar7[2] = uVar8;
  }
  puVar7[2] = 0;
  puVar7[3] = puVar7[3] & 0xffffffe0 | 3;
  uVar4 = 0x6f;
  if (*(int *)(param_1 + 0x24) != 0) {
    uVar4 = 0x7f;
  }
  puVar7[2] = uVar4;
  uVar4 = FUN_1000433c(param_1);
  *(uint *)(param_1 + 0x30) = uVar4;
  iVar3 = *(int *)(*(int *)(param_1 + 4) + 0x9c);
  iVar5 = *(int *)(*(int *)(param_1 + 4) + 0xa0);
  if (iVar3 == 1) {
    uVar8 = uVar4;
    if ((uVar4 & 0x80000000) != 0) {
      uVar8 = uVar4 + 3;
    }
    *(int *)(param_1 + 0x38) = (int)uVar8 >> 2;
  }
  else if (iVar3 == 0) {
    *(undefined4 *)(param_1 + 0x38) = 1;
  }
  else if (iVar3 == 2) {
    *(int *)(param_1 + 0x38) = (int)uVar4 / 2;
  }
  else if (iVar3 == 3) {
    *(uint *)(param_1 + 0x38) = uVar4 - 2;
  }
  if (iVar5 == 1) {
    uVar6 = 2;
  }
  else {
    uVar6 = 0;
    if (iVar5 != 0) {
      if (iVar5 == 2) {
        if ((uVar4 & 0x80000000) != 0) {
          uVar4 = uVar4 + 3;
        }
        *(int *)(param_1 + 0x34) = (int)uVar4 >> 2;
      }
      else if (iVar5 == 3) {
        *(int *)(param_1 + 0x34) = (int)uVar4 / 2;
      }
      goto LAB_1000444c;
    }
  }
  *(undefined4 *)(param_1 + 0x34) = uVar6;
LAB_1000444c:
  *(undefined4 *)(param_1 + 0x2c) = 1;
  *(undefined4 *)(param_1 + 0x68) = 0xffffffff;
  *(undefined4 *)(param_1 + 0x7c) = 0xffffffff;
  gx8002_backup_request_irq(*(undefined4 *)(param_1 + 0x3c),PTR_LAB_10004518,param_1);
  return 0;
}

