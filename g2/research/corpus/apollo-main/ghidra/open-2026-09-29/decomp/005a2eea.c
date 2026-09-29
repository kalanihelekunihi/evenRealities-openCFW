
ulonglong FUN_005a2eea(int param_1,int param_2,undefined4 param_3)

{
  undefined1 uVar1;
  uint *puVar2;
  int iVar3;
  uint *puVar4;
  uint *puVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  bool bVar13;
  
  puVar4 = (uint *)(DAT_005a36a4 + param_1 * 4 + 4);
  puVar5 = (uint *)(DAT_005a36a4 + 100);
  uVar1 = *(undefined1 *)puVar5;
  uVar7 = *puVar5;
  uVar8 = *puVar5;
  uVar6 = *puVar5;
  uVar9 = *(byte *)(DAT_005a36a4 + param_2 * 4 + 4) & 0x7f;
  uVar10 = (*puVar4 & 0xfffffff) >> 0x15;
  uVar11 = *(byte *)puVar4 & 0x7f;
  if (*DAT_005a36a8 << 0x1f < 0) {
    uVar12 = 0;
    while ((uVar12 < 0x3c && (-1 < *DAT_005a3780 << 1))) {
      FUN_004807a0(1);
      uVar12 = uVar12 + 1;
    }
    FUN_005a40ca();
  }
  *DAT_005a3784 = param_3;
  *DAT_005a3788 = param_1;
  *DAT_005a378c = (*puVar4 & 0x1ffff) >> 7;
  *DAT_005a3790 = (*puVar4 & 0x1fffff) >> 0x11;
  *DAT_005a3794 = uVar10;
  *DAT_005a35a0 = uVar11;
  puVar5 = DAT_005a3260;
  *DAT_005a3260 = *DAT_005a3260 & 0xfffffffc | 1;
  uVar12 = 0;
  while ((puVar2 = DAT_005a3aa4, uVar12 < 0x14 && ((*puVar5 & 7) >> 2 == 0))) {
    FUN_004807a0(1);
    uVar12 = uVar12 + 1;
  }
  *DAT_005a3aa4 = *DAT_005a3aa4 & 0xffffffbf;
  *puVar2 = *puVar2 & 0xfffffff7;
  *puVar2 = *puVar2 | 0x2000000;
  puVar2 = DAT_005a3264;
  bVar13 = -1 < (int)(*DAT_005a3264 << 0x1a);
  if (bVar13) {
    *DAT_005a3264 = *DAT_005a3264 | 0x20;
    FUN_004807a0(1);
    FUN_004807fc(0xf,DAT_005a3268,0x1000000,0x1000000);
  }
  if (*DAT_005a3268 << 7 < 0) {
    *puVar5 = *puVar5 & 0xfffffffc | 2;
    uVar12 = 0;
    while ((uVar12 < 0x14 && ((*puVar5 & 7) >> 2 == 0))) {
      FUN_004807a0(1);
      uVar12 = uVar12 + 1;
    }
  }
  if (bVar13) {
    *puVar2 = *puVar2 & 0xffffffdf;
  }
  puVar5 = DAT_005a3aa8;
  *DAT_005a3aa8 = *DAT_005a3aa8 & 0xffffc3ff | ((*puVar4 & 0x1fffff) >> 0x11) << 10;
  *puVar5 = (*puVar4 & 0x1ffff) >> 7 | *puVar5 & 0xfffffc00;
  *DAT_005a3aac = uVar10 | *DAT_005a3aac & 0xffffff80;
  if ((int)(uVar11 - uVar9) < 1) {
    iVar3 = 0;
  }
  else {
    iVar3 = (uVar11 - uVar9) * 2;
  }
  if (iVar3 + uVar9 < 0x80) {
    *DAT_005a3e20 = *DAT_005a3e20 & 0xffffff80 | iVar3 + uVar9 & 0x7f;
  }
  else {
    *DAT_005a3e20 = *DAT_005a3e20 | 0x7f;
  }
  FUN_004807a0(0x32);
  *DAT_005a3e20 = uVar11 | *DAT_005a3e20 & 0xffffff80;
  FUN_005a423c(param_3,param_1);
  return CONCAT17((char)(uVar6 >> 0x15),
                  CONCAT16((char)(uVar8 >> 0xe),CONCAT15((char)(uVar7 >> 7),CONCAT14(uVar1,puVar4)))
                 ) & 0x7f7f7f7fffffffff;
}

