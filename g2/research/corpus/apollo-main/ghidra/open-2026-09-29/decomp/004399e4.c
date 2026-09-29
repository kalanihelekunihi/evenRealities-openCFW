
void FUN_004399e4(int param_1)

{
  int iVar1;
  uint uVar2;
  undefined1 *puVar3;
  byte *pbVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  
  for (iVar8 = (*(int *)(param_1 + 0x34) - *(int *)(param_1 + 0x30)) * 8 - *(int *)(param_1 + 0x20);
      0 < iVar8; iVar8 = iVar8 + -0x20) {
    iVar1 = 0x20;
    if (iVar8 < 0x21) {
      iVar1 = iVar8;
    }
    iVar1 = iVar1 + *(int *)(param_1 + 0x20);
    if (iVar1 < 0x21) {
      *(int *)(param_1 + 0x20) = iVar1;
    }
    else {
      FUN_00439b12(param_1,0);
    }
  }
  FUN_0043992c(param_1 + 0x1c,param_1 + 0x28);
  iVar8 = FUN_004397d0(param_1 + 4);
  uVar5 = *(uint *)(param_1 + 4);
  uVar9 = -iVar8 + 0x19;
  uVar2 = 0xffffff >> (uVar9 & 0xff);
  uVar7 = *(int *)(param_1 + 8) + uVar5;
  uVar6 = uVar2 + uVar5 & ~uVar2 & 0xffffff;
  if (-((int)~-(uint)(uVar2 + uVar5 >> 0x18 == 0) >> 0x1f) ==
      -((int)~-(uint)(uVar7 >> 0x18 == 0) >> 0x1f)) {
    if ((uVar7 & 0xffffff) <= uVar2 + uVar6) {
      uVar9 = -iVar8 + 0x1a;
      uVar6 = uVar5 + (uVar2 >> 1) & ~(uVar2 >> 1) & 0xffffff;
    }
    *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) | -(uint)(uVar6 < uVar5) >> 0x1f;
  }
  *(uint *)(param_1 + 4) = uVar6;
  for (; 8 < (int)uVar9; uVar9 = uVar9 - 8) {
    FUN_0043996c(param_1 + 4,param_1 + 0x28);
  }
  FUN_0043996c(param_1 + 4,param_1 + 0x28);
  iVar8 = *(int *)(param_1 + 0xc) >> (8 - uVar9 & 0xff);
  if (*(int *)(param_1 + 0x14) != 0) {
    puVar3 = *(undefined1 **)(param_1 + 0x30);
    if (puVar3 < *(undefined1 **)(param_1 + 0x2c)) {
      *(undefined1 **)(param_1 + 0x30) = puVar3 + 1;
      *puVar3 = (char)*(int *)(param_1 + 0xc);
    }
    iVar8 = *(int *)(param_1 + 0x14);
    while (1 < iVar8) {
      if (*(uint *)(param_1 + 0x30) < *(uint *)(param_1 + 0x2c)) {
        puVar3 = *(undefined1 **)(param_1 + 0x30);
        *(undefined1 **)(param_1 + 0x30) = puVar3 + 1;
        *puVar3 = 0xff;
      }
      iVar8 = *(int *)(param_1 + 0x14) + -1;
      *(int *)(param_1 + 0x14) = iVar8;
    }
    if ((int)uVar9 < 8) {
      iVar8 = 0;
    }
    else {
      iVar8 = 0xff;
    }
  }
  pbVar4 = *(byte **)(param_1 + 0x30);
  if (pbVar4 < *(byte **)(param_1 + 0x2c)) {
    *pbVar4 = *pbVar4 & (byte)(0xff >> (uVar9 & 0xff));
    **(byte **)(param_1 + 0x30) = (byte)(iVar8 << (8 - uVar9 & 0xff)) | **(byte **)(param_1 + 0x30);
  }
  return;
}

