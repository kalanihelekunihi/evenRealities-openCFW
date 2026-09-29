
ulonglong FUN_005a326c(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  uint *puVar3;
  uint *puVar4;
  uint uVar5;
  uint uVar6;
  uint extraout_r3;
  uint *puVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  bool bVar13;
  uint in_fpscr;
  float fVar14;
  int iVar15;
  
  iVar15 = DAT_005a36a4;
  puVar7 = (uint *)(DAT_005a36a4 + param_1 * 4 + 4);
  puVar3 = (uint *)(DAT_005a36a4 + param_2 * 4 + 4);
  puVar4 = (uint *)(DAT_005a36a4 + 100);
  bVar1 = *(byte *)puVar4 & 0x7f;
  uVar8 = *puVar4;
  uVar9 = *puVar4;
  uVar5 = *puVar4;
  uVar6 = *(byte *)puVar3 & 0x7f;
  uVar10 = (*puVar3 & 0xfffffff) >> 0x15;
  uVar11 = (*puVar7 & 0xfffffff) >> 0x15;
  uVar12 = *(byte *)puVar7 & 0x7f;
  if (*DAT_005a36a8 << 0x1f < 0) {
    uVar6 = 0;
    while ((uVar6 < 0x3c && (-1 < *DAT_005a3780 << 1))) {
      FUN_004807a0(1);
      uVar6 = uVar6 + 1;
    }
    FUN_005a40ca();
    uVar6 = extraout_r3;
  }
  *DAT_005a3784 = param_3;
  *DAT_005a3788 = param_1;
  *DAT_005a378c = (*puVar7 & 0x1ffff) >> 7;
  puVar3 = DAT_005a3790;
  *DAT_005a3790 = (*puVar7 & 0x1fffff) >> 0x11;
  *DAT_005a3794 = uVar11;
  *DAT_005a35a0 = uVar12;
  FUN_005a423c(param_3,param_1,puVar3,uVar6,param_2,bVar1,param_4);
  fVar14 = (float)VectorUnsignedToFloat
                            (uVar12 - (*(byte *)(iVar15 + 8) & 0x7f),(byte)(in_fpscr >> 0x16) & 3);
  iVar15 = (uint)(0.0 < fVar14 * DAT_005a359c) * (int)(fVar14 * DAT_005a359c);
  if (iVar15 + uVar12 < 0x80) {
    *DAT_005a3aa0 = *DAT_005a3aa0 & 0xffffff80 | iVar15 + uVar12 & 0x7f;
  }
  else {
    *DAT_005a3aa0 = *DAT_005a3aa0 | 0x7f;
  }
  if ((int)(uVar11 - uVar10) < 1) {
    iVar2 = 0;
  }
  else {
    iVar2 = (uVar11 - uVar10) * 2;
  }
  if (iVar2 + uVar10 < 0x80) {
    *DAT_005a3aac = *DAT_005a3aac & 0xffffff80 | iVar2 + uVar10 & 0x7f;
  }
  else {
    *DAT_005a3aac = *DAT_005a3aac | 0x7f;
  }
  FUN_004807a0(0x32);
  *DAT_005a3aac = uVar11 | *DAT_005a3aac & 0xffffff80;
  puVar3 = DAT_005a3aa8;
  *DAT_005a3aa8 = *DAT_005a3aa8 & 0xffffc3ff | ((*puVar7 & 0x1fffff) >> 0x11) << 10;
  *puVar3 = (*puVar7 & 0x1ffff) >> 7 | *puVar3 & 0xfffffc00;
  FUN_004807a0(5);
  *DAT_005a3aa0 = uVar12 | *DAT_005a3aa0 & 0xffffff80;
  puVar3 = DAT_005a3e78;
  *DAT_005a3e78 = *DAT_005a3e78 & 0xfffffffc | 1;
  uVar6 = 0;
  while ((puVar4 = DAT_005a3aa4, uVar6 < 0x14 && ((*puVar3 & 7) >> 2 == 0))) {
    FUN_004807a0(1);
    uVar6 = uVar6 + 1;
  }
  *DAT_005a3aa4 = *DAT_005a3aa4 | 0x40;
  *puVar4 = *puVar4 | 8;
  *puVar4 = *puVar4 & 0xfdffffff;
  puVar4 = DAT_005a3e7c;
  bVar13 = -1 < (int)(*DAT_005a3e7c << 0x1a);
  if (bVar13) {
    *DAT_005a3e7c = *DAT_005a3e7c | 0x20;
    FUN_004807a0(1);
    FUN_004807fc(0xf,DAT_005a40f8,0x1000000,0x1000000);
  }
  if (*DAT_005a40f8 << 7 < 0) {
    *puVar3 = *puVar3 & 0xfffffffc | 2;
    uVar6 = 0;
    while ((uVar6 < 0x14 && ((*puVar3 & 7) >> 2 == 0))) {
      FUN_004807a0(1);
      uVar6 = uVar6 + 1;
    }
  }
  if (bVar13) {
    *puVar4 = *puVar4 & 0xffffffdf;
  }
  return CONCAT17((char)(uVar5 >> 0x15),
                  CONCAT16((char)(uVar9 >> 0xe),CONCAT15((char)(uVar8 >> 7),CONCAT14(bVar1,iVar15)))
                 ) & 0x7f7f7fffffffffff;
}

