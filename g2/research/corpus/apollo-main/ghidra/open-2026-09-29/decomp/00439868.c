
void FUN_00439868(undefined1 *param_1,int param_2,int param_3,int param_4)

{
  uint *puVar1;
  byte *pbVar2;
  byte *pbVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  undefined4 uVar7;
  int iVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  undefined4 uVar13;
  undefined4 uVar14;
  
  uVar9 = *DAT_00439910;
  uVar10 = DAT_00439910[1];
  uVar11 = DAT_00439910[2];
  uVar12 = DAT_00439910[3];
  uVar13 = DAT_00439910[4];
  uVar14 = DAT_00439910[5];
  if (param_2 == 0) {
    uVar7 = 0x20;
  }
  else {
    uVar7 = 0;
  }
  *param_1 = (char)param_2;
  *(undefined4 *)(param_1 + 4) = uVar9;
  *(undefined4 *)(param_1 + 8) = uVar10;
  *(undefined4 *)(param_1 + 0xc) = uVar11;
  *(undefined4 *)(param_1 + 0x10) = uVar12;
  *(undefined4 *)(param_1 + 0x14) = uVar13;
  *(undefined4 *)(param_1 + 0x18) = uVar14;
  *(int *)(param_1 + 0x28) = param_3;
  *(int *)(param_1 + 0x30) = param_3;
  *(undefined4 *)(param_1 + 0x1c) = 0;
  *(undefined4 *)(param_1 + 0x20) = uVar7;
  *(undefined4 *)(param_1 + 0x24) = 0;
  *(int *)(param_1 + 0x2c) = param_3 + param_4;
  *(int *)(param_1 + 0x34) = param_3 + param_4;
  if (param_2 == 0) {
    pbVar2 = *(byte **)(param_1 + 0x2c);
    pbVar3 = *(byte **)(param_1 + 0x30);
    if (pbVar3 < pbVar2) {
      *(byte **)(param_1 + 0x30) = pbVar3 + 1;
      iVar4 = (uint)*pbVar3 << 0x10;
    }
    else {
      iVar4 = 0;
    }
    *(int *)(param_1 + 4) = iVar4;
    if (*(byte **)(param_1 + 0x30) < pbVar2) {
      pbVar3 = *(byte **)(param_1 + 0x30);
      *(byte **)(param_1 + 0x30) = pbVar3 + 1;
      uVar5 = (uint)*pbVar3 << 8;
    }
    else {
      uVar5 = 0;
    }
    *(uint *)(param_1 + 4) = uVar5 | *(uint *)(param_1 + 4);
    if (*(byte **)(param_1 + 0x30) < pbVar2) {
      pbVar2 = *(byte **)(param_1 + 0x30);
      *(byte **)(param_1 + 0x30) = pbVar2 + 1;
      uVar5 = (uint)*pbVar2;
    }
    else {
      uVar5 = 0;
    }
    *(uint *)(param_1 + 4) = uVar5 | *(uint *)(param_1 + 4);
    puVar1 = (uint *)(param_1 + 0x1c);
    iVar8 = *(int *)(param_1 + 0x20) >> 3;
    iVar4 = *(int *)(param_1 + 0x34) - *(int *)(param_1 + 0x28);
    if (iVar8 < *(int *)(param_1 + 0x34) - *(int *)(param_1 + 0x28)) {
      iVar4 = iVar8;
    }
    uVar5 = *puVar1;
    uVar6 = *(int *)(param_1 + 0x20) + iVar4 * -8;
    *(uint *)(param_1 + 0x20) = uVar6;
    for (; iVar4 != 0; iVar4 = iVar4 + -1) {
      iVar8 = *(int *)(param_1 + 0x34);
      *(byte **)(param_1 + 0x34) = (byte *)(iVar8 + -1);
      *puVar1 = uVar5 >> 8;
      uVar5 = uVar5 >> 8 | (uint)*(byte *)(iVar8 + -1) << 0x18;
    }
    if (7 < (int)uVar6) {
      iVar4 = *(int *)(param_1 + 0x20) + *(int *)(param_1 + 0x24);
      if (0x20 < iVar4) {
        iVar4 = 0x20;
      }
      *(int *)(param_1 + 0x24) = iVar4;
      uVar5 = uVar5 >> (uVar6 & 0xff);
      *(undefined4 *)(param_1 + 0x20) = 0;
    }
    *puVar1 = uVar5;
    return;
  }
  return;
}

