
longlong FUN_004fc644(uint param_1)

{
  byte bVar1;
  float fVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  int iVar8;
  int *piVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  int iVar13;
  uint uVar14;
  int iVar15;
  uint in_fpscr;
  int iVar16;
  uint uVar17;
  float fVar18;
  float fVar19;
  undefined1 auStack_70 [64];
  
  FUN_0043c0e4(DAT_004fc904,auStack_70,0x40,0);
  uVar10 = FUN_0043de82(param_1);
  *DAT_004fd454 = uVar10;
  FUN_0043f4c0(*DAT_004fd454,0x240,0x100);
  FUN_0043f09a(*DAT_004fd454,0,0x10);
  FUN_0043ded4(*DAT_004fd454,0x10);
  FUN_0044e3ca(*DAT_004fd454,0xc);
  FUN_0044e368(*DAT_004fd454,0);
  FUN_004fb1c0(*DAT_004fd454,0,0);
  FUN_0044131c(*DAT_004fd454,0,0);
  uVar10 = FUN_0044104c(0);
  FUN_0044127e(*DAT_004fd454,uVar10,0);
  FUN_0044129e(*DAT_004fd454,0,0);
  for (iVar13 = 0; puVar4 = DAT_004fd5b0, puVar3 = DAT_004fd458, iVar13 < 2; iVar13 = iVar13 + 1) {
    uVar10 = FUN_0043de82(*DAT_004fd454);
    puVar3[iVar13] = uVar10;
    FUN_0043f4c0(puVar3[iVar13],0x218,0x100);
    FUN_0043f09a(puVar3[iVar13],0x14,iVar13 << 8);
    FUN_0043dfa4(puVar3[iVar13],0x10);
    FUN_0044e368(puVar3[iVar13],0);
    uVar10 = FUN_0044104c(0);
    FUN_0044127e(puVar3[iVar13],uVar10,0);
    FUN_0044129e(puVar3[iVar13],0,0);
    FUN_004fb1c0(puVar3[iVar13],0,0);
    FUN_0044131c(puVar3[iVar13],0,0);
    FUN_0044146a(puVar3[iVar13],0,0);
  }
  uVar10 = FUN_00498668(*DAT_004fd458);
  *puVar4 = uVar10;
  health_lock_storage();
  iVar13 = DAT_004fd5b8;
  if (*(char *)(DAT_004fd5b8 + 0xc0) == '\x01') {
    FUN_00498680(*puVar4,DAT_004fd5bc);
  }
  else if (*(char *)(DAT_004fd5b8 + 0xc0) == '\x03') {
    FUN_00498680(*puVar4,DAT_004fd5c0);
  }
  else {
    FUN_00498680(*puVar4,DAT_004fd5c4);
  }
  health_unlock_storage();
  FUN_0043f506(*puVar4,0x18);
  FUN_0043f568(*puVar4,0x18);
  FUN_0043f0e0(*puVar4,0);
  FUN_0043f142(*puVar4,2);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar5 = DAT_004fd5cc;
  uVar10 = FUN_00499416(*puVar3);
  *puVar5 = uVar10;
  FUN_0043f506(*puVar5,0x3fffffff);
  FUN_0043f568(*puVar5,0x3fffffff);
  FUN_0043f6d6(*puVar5,*puVar4,0x13,8,0xfffffffe);
  uVar10 = DAT_004fd6b8;
  uVar11 = FUN_00460084(DAT_004fd6b8);
  uVar10 = FUN_0045fffe(uVar10,uVar11);
  FUN_0049942e(*puVar5,uVar10);
  uVar10 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar5,uVar10,0);
  puVar4 = DAT_004fd6bc;
  FUN_0044143e(*puVar5,*DAT_004fd6bc,0);
  health_lock_storage();
  iVar16 = (uint)(0.0 < *(float *)(iVar13 + 0xb4)) * (int)*(float *)(iVar13 + 0xb4);
  health_unlock_storage();
  if (iVar16 == 0) {
    FUN_004b4728(auStack_70,&DAT_004fcbb4);
  }
  else {
    FUN_004b4728(auStack_70,&DAT_004fcbb0,iVar16);
  }
  puVar5 = DAT_004fd6c0;
  uVar10 = FUN_00499416(*puVar3);
  *puVar5 = uVar10;
  FUN_0043f506(*puVar5,0x3fffffff);
  FUN_0043f568(*puVar5,0x3fffffff);
  FUN_0043f6b8(*puVar5,3,0,0);
  FUN_0049942e(*puVar5,auStack_70);
  uVar10 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar5,uVar10,0);
  FUN_0044143e(*puVar5,*puVar4,0);
  health_lock_storage();
  uVar17 = (uint)(0.0 < *(float *)(iVar13 + 0xc)) * (int)*(float *)(iVar13 + 0xc);
  if (*(int *)(iVar13 + 8) == 0) {
    uVar14 = 10000;
  }
  else {
    uVar14 = *(uint *)(iVar13 + 8);
  }
  health_unlock_storage();
  puVar5 = DAT_004fd788;
  uVar10 = FUN_00498668(*puVar3);
  *puVar5 = uVar10;
  FUN_00498680(*puVar5,DAT_004fd78c);
  FUN_0043f506(*puVar5,0x18);
  FUN_0043f568(*puVar5,0x18);
  FUN_0043f0e0(*puVar5,0);
  FUN_0043f142(*puVar5,0x37);
  FUN_0043ded4(*puVar5,0x10000);
  FUN_0043dfa4(*puVar5,0x10);
  puVar6 = DAT_004fd790;
  uVar10 = FUN_00499416(*puVar3);
  *puVar6 = uVar10;
  FUN_0043f506(*puVar6,0x240);
  FUN_0043f568(*puVar6,0x3fffffff);
  FUN_0043f6d6(*puVar6,*puVar5,0x13,8,0xfffffffe);
  uVar10 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar6,uVar10,0);
  FUN_0044143e(*puVar6,*puVar4,0);
  if (uVar17 == 0) {
    uVar10 = FUN_00460084(DAT_004fd794);
    uVar10 = FUN_0045fffe(DAT_004fd794,uVar10);
    FUN_004b4728(auStack_70,DAT_004fd79c,uVar10);
  }
  else {
    uVar10 = FUN_00460084(DAT_004fd794);
    uVar10 = FUN_0045fffe(DAT_004fd794,uVar10);
    FUN_004b4728(auStack_70,DAT_004fd798,uVar10,uVar17);
  }
  FUN_0049942e(*puVar6,auStack_70);
  puVar6 = DAT_004fd7a0;
  uVar10 = FUN_00499416(*puVar3);
  *puVar6 = uVar10;
  FUN_0043f506(*puVar6,0x3fffffff);
  FUN_0043f568(*puVar6,0x3fffffff);
  FUN_0043f6b8(*puVar6,3,0,0x35);
  FUN_004b4728(auStack_70,&DAT_004fcbb0,uVar14);
  FUN_0049942e(*puVar6,auStack_70);
  uVar10 = FUN_0044104c(DAT_004fd7a4);
  FUN_0044140e(*puVar6,uVar10,0);
  FUN_0044143e(*puVar6,*puVar4,0);
  puVar6 = DAT_004fd838;
  uVar10 = FUN_00498668(*puVar3);
  *puVar6 = uVar10;
  FUN_00498680(*puVar6,DAT_004fd7a8);
  FUN_0043f506(*puVar6,0x218);
  FUN_0043f568(*puVar6,8);
  FUN_0043f6d6(*puVar6,*puVar5,0xd,0,10);
  FUN_0043ded4(*puVar6,0x10000);
  FUN_0043dfa4(*puVar6,0x10);
  puVar5 = DAT_004fd7ac;
  fVar2 = DAT_004fcd90;
  fVar18 = DAT_004fcd8c;
  if (uVar17 != 0) {
    if (uVar17 < uVar14) {
      fVar18 = (float)VectorUnsignedToFloat(uVar17,(byte)(in_fpscr >> 0x16) & 3);
      fVar19 = (float)VectorUnsignedToFloat(uVar14,(byte)(in_fpscr >> 0x16) & 3);
      fVar18 = fVar18 / fVar19;
    }
    else {
      fVar18 = 1.0;
    }
  }
  iVar16 = ((int)(fVar18 * DAT_004fcd90 + 1.0) / 3) * 3;
  if (0x218 < iVar16) {
    iVar16 = 0x218;
  }
  uVar10 = FUN_0043de82(*puVar3);
  *puVar5 = uVar10;
  FUN_0043f506(*puVar5,0x218 - iVar16);
  FUN_0043f568(*puVar5,8);
  FUN_0043f6d6(*puVar5,*puVar6,1,iVar16,0);
  uVar10 = FUN_0044104c(0);
  FUN_0044127e(*puVar5,uVar10,0);
  FUN_0044129e(*puVar5,0xbe,0);
  FUN_004fb1c0(*puVar5,0,0);
  FUN_0044131c(*puVar5,0,0);
  FUN_0044146a(*puVar5,0,0);
  FUN_0043dfa4(*puVar5,0x10);
  health_lock_storage();
  uVar17 = (uint)(0.0 < *(float *)(iVar13 + 0x24)) * (int)*(float *)(iVar13 + 0x24);
  if (*(int *)(iVar13 + 0x20) == 0) {
    uVar14 = 2000;
  }
  else {
    uVar14 = *(uint *)(iVar13 + 0x20);
  }
  health_unlock_storage();
  puVar5 = DAT_004fd83c;
  uVar10 = FUN_00498668(*puVar3);
  *puVar5 = uVar10;
  FUN_00498680(*puVar5,DAT_004fd870);
  FUN_0043f506(*puVar5,0x18);
  FUN_0043f568(*puVar5,0x18);
  FUN_0043f0e0(*puVar5,0);
  FUN_0043f142(*puVar5,0x75);
  FUN_0043ded4(*puVar5,0x10000);
  FUN_0043dfa4(*puVar5,0x10);
  puVar6 = DAT_004fd874;
  uVar10 = FUN_00499416(*puVar3);
  *puVar6 = uVar10;
  FUN_0043f506(*puVar6,0x240);
  FUN_0043f568(*puVar6,0x3fffffff);
  FUN_0043f6d6(*puVar6,*puVar5,0x13,8,0xfffffffe);
  uVar10 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar6,uVar10,0);
  FUN_0044143e(*puVar6,*puVar4,0);
  if (uVar17 == 0) {
    uVar10 = FUN_00460084(DAT_004fd878);
    uVar10 = FUN_0045fffe(DAT_004fd878,uVar10);
    FUN_004b4728(auStack_70,DAT_004fd79c,uVar10);
  }
  else {
    uVar10 = FUN_00460084(DAT_004fd878);
    uVar10 = FUN_0045fffe(DAT_004fd878,uVar10);
    FUN_004b4728(auStack_70,DAT_004fd798,uVar10,uVar17);
  }
  FUN_0049942e(*puVar6,auStack_70);
  puVar6 = DAT_004fd87c;
  uVar10 = FUN_00499416(*puVar3);
  *puVar6 = uVar10;
  FUN_0043f506(*puVar6,0x3fffffff);
  FUN_0043f568(*puVar6,0x3fffffff);
  FUN_0043f6b8(*puVar6,3,0,0x73);
  FUN_004b4728(auStack_70,&DAT_004fcfd4,uVar14);
  FUN_0049942e(*puVar6,auStack_70);
  uVar10 = FUN_0044104c(DAT_004fd7a4);
  FUN_0044140e(*puVar6,uVar10,0);
  FUN_0044143e(*puVar6,*puVar4,0);
  puVar6 = DAT_004fd880;
  uVar10 = FUN_00498668(*puVar3);
  *puVar6 = uVar10;
  FUN_00498680(*puVar6,DAT_004fd7a8);
  FUN_0043f506(*puVar6,0x218);
  FUN_0043f568(*puVar6,8);
  FUN_0043f6d6(*puVar6,*puVar5,0xd,0,10);
  FUN_0043ded4(*puVar6,0x10000);
  FUN_0043dfa4(*puVar6,0x10);
  puVar5 = DAT_004fd884;
  fVar18 = DAT_004fcd8c;
  if (uVar17 != 0) {
    if (uVar17 < uVar14) {
      fVar18 = (float)VectorUnsignedToFloat(uVar17,(byte)(in_fpscr >> 0x16) & 3);
      fVar19 = (float)VectorUnsignedToFloat(uVar14,(byte)(in_fpscr >> 0x16) & 3);
      fVar18 = fVar18 / fVar19;
    }
    else {
      fVar18 = 1.0;
    }
  }
  iVar16 = ((int)(fVar18 * fVar2 + 1.0) / 3) * 3;
  if (0x218 < iVar16) {
    iVar16 = 0x218;
  }
  uVar10 = FUN_0043de82(*puVar3);
  *puVar5 = uVar10;
  FUN_0043f506(*puVar5,0x218 - iVar16);
  FUN_0043f568(*puVar5,8);
  FUN_0043f6d6(*puVar5,*puVar6,1,iVar16,0);
  uVar10 = FUN_0044104c(0);
  FUN_0044127e(*puVar5,uVar10,0);
  FUN_0044129e(*puVar5,0xbe,0);
  FUN_004fb1c0(*puVar5,0,0);
  FUN_0044131c(*puVar5,0,0);
  FUN_0044146a(*puVar5,0,0);
  FUN_0043dfa4(*puVar5,0x10);
  puVar5 = DAT_004fd888;
  uVar10 = FUN_00498668(*puVar3);
  *puVar5 = uVar10;
  FUN_00498680(*puVar5,DAT_004fd88c);
  FUN_0043f506(*puVar5,0x18);
  FUN_0043f568(*puVar5,0x18);
  FUN_0043f0e0(*puVar5,0);
  FUN_0043f142(*puVar5,0xbf);
  FUN_0043ded4(*puVar5,0x10000);
  FUN_0043dfa4(*puVar5,0x10);
  puVar6 = DAT_004fd890;
  uVar10 = FUN_00499416(*puVar3);
  *puVar6 = uVar10;
  FUN_0043f506(*puVar6,0xa3);
  FUN_0043f568(*puVar6,0x3fffffff);
  FUN_0043f6d6(*puVar6,*puVar5,0x13,8,0xfffffffe);
  health_lock_storage();
  if (*(float *)(iVar13 + 0x3c) <= 0.0) {
    FUN_004b4728(auStack_70,&DAT_004fd1ec);
  }
  else {
    FUN_004b4728(auStack_70,&DAT_004fcfd4,
                 (uint)(0.0 < *(float *)(iVar13 + 0x3c)) * (int)*(float *)(iVar13 + 0x3c));
  }
  FUN_0049942e(*puVar6,auStack_70);
  health_unlock_storage();
  uVar10 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar6,uVar10,0);
  FUN_0044143e(*puVar6,*puVar4,0);
  puVar7 = DAT_004fd894;
  uVar10 = FUN_00499416(*puVar3);
  *puVar7 = uVar10;
  FUN_0043f506(*puVar7,0xa3);
  FUN_0043f568(*puVar7,0x3fffffff);
  FUN_0043f6d6(*puVar7,*puVar6,0xd,0,4);
  health_lock_storage();
  uVar10 = DAT_004fd898;
  if (*(int *)(iVar13 + 0x44) == 0) {
    uVar11 = FUN_00460084(DAT_004fd898);
    uVar11 = FUN_0045fffe(uVar10,uVar11);
    uVar10 = DAT_004fd89c;
    uVar12 = FUN_00460084(DAT_004fd89c);
    uVar10 = FUN_0045fffe(uVar10,uVar12);
    FUN_004b4728(auStack_70,DAT_004fd8a0,uVar10,uVar11);
  }
  else if (*(uint *)(iVar13 + 0x44) < 0x3c) {
    uVar11 = FUN_00460084(DAT_004fd898);
    uVar11 = FUN_0045fffe(uVar10,uVar11);
    uVar10 = DAT_004fd89c;
    uVar12 = FUN_00460084(DAT_004fd89c);
    uVar10 = FUN_0045fffe(uVar10,uVar12);
    FUN_004b4728(auStack_70,DAT_004fd8a4,uVar10,uVar11);
  }
  else {
    uVar17 = *(uint *)(iVar13 + 0x44);
    uVar14 = *(uint *)(iVar13 + 0x44);
    uVar11 = FUN_00460084(DAT_004fd898);
    uVar11 = FUN_0045fffe(uVar10,uVar11);
    uVar10 = DAT_004fd89c;
    uVar12 = FUN_00460084(DAT_004fd89c);
    uVar10 = FUN_0045fffe(uVar10,uVar12);
    FUN_004b4728(auStack_70,DAT_004fd8a8,uVar17 / 0xe10,uVar10,(uVar14 % 0xe10) / 0x3c,uVar11);
  }
  FUN_0049942e(*puVar7,auStack_70);
  health_unlock_storage();
  FUN_0044143e(*puVar7,*puVar4,0);
  uVar10 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar7,uVar10,0);
  puVar6 = DAT_004fd8ac;
  uVar10 = FUN_00498668(*puVar3);
  *puVar6 = uVar10;
  FUN_00498680(*puVar6,DAT_004fd8b0);
  FUN_0043f506(*puVar6,0x18);
  FUN_0043f568(*puVar6,0x18);
  FUN_0043f6d6(*puVar6,*puVar5,0x13,0xb2,0);
  FUN_0043ded4(*puVar6,0x10000);
  FUN_0043dfa4(*puVar6,0x10);
  puVar5 = DAT_004fd8b4;
  uVar10 = FUN_00499416(*puVar3);
  *puVar5 = uVar10;
  FUN_0043f506(*puVar5,0xab);
  FUN_0043f568(*puVar5,0x3fffffff);
  FUN_0043f6d6(*puVar5,*puVar6,0x13,8,0xfffffffe);
  health_lock_storage();
  uVar10 = DAT_004fd8b8;
  if (*(float *)(iVar13 + 0x54) <= 0.0) {
    uVar11 = FUN_00460084(DAT_004fd8b8);
    uVar10 = FUN_0045fffe(uVar10,uVar11);
    FUN_004b4728(auStack_70,&DAT_004fd450,uVar10);
  }
  else {
    uVar11 = FUN_00460084(DAT_004fd8b8);
    uVar10 = FUN_0045fffe(uVar10,uVar11);
    FUN_004b4728(auStack_70,DAT_004fd8bc,
                 (uint)(0.0 < *(float *)(iVar13 + 0x54)) * (int)*(float *)(iVar13 + 0x54),uVar10);
  }
  FUN_0049942e(*puVar5,auStack_70);
  health_unlock_storage();
  uVar10 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar5,uVar10,0);
  FUN_0044143e(*puVar5,*puVar4,0);
  puVar7 = DAT_004fd8c0;
  uVar10 = FUN_00499416(*puVar3);
  *puVar7 = uVar10;
  FUN_0043f506(*puVar7,0xab);
  FUN_0043f568(*puVar7,0x3fffffff);
  FUN_0043f6d6(*puVar7,*puVar5,0xd,0,4);
  health_lock_storage();
  uVar10 = DAT_004fd8b8;
  if (*(float *)(iVar13 + 0x58) <= 0.0) {
    uVar11 = FUN_00460084(DAT_004fd8b8);
    uVar11 = FUN_0045fffe(uVar10,uVar11);
    uVar10 = DAT_004fd8c4;
    uVar12 = FUN_00460084(DAT_004fd8c4);
    uVar10 = FUN_0045fffe(uVar10,uVar12);
    FUN_004b4728(auStack_70,DAT_004fd8cc,uVar10,uVar11);
  }
  else {
    uVar11 = FUN_00460084(DAT_004fd8b8);
    uVar11 = FUN_0045fffe(uVar10,uVar11);
    uVar10 = DAT_004fd8c4;
    uVar12 = FUN_00460084(DAT_004fd8c4);
    uVar10 = FUN_0045fffe(uVar10,uVar12);
    FUN_004b4728(auStack_70,DAT_004fd8c8,uVar10,
                 (uint)(0.0 < *(float *)(iVar13 + 0x58)) * (int)*(float *)(iVar13 + 0x58),uVar11);
  }
  FUN_0049942e(*puVar7,auStack_70);
  health_unlock_storage();
  uVar10 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar7,uVar10,0);
  FUN_0044143e(*puVar7,*puVar4,0);
  puVar5 = DAT_004fd8d0;
  uVar10 = FUN_00498668(*puVar3);
  *puVar5 = uVar10;
  FUN_00498680(*puVar5,DAT_004fd8d4);
  FUN_0043f506(*puVar5,0x18);
  FUN_0043f568(*puVar5,0x18);
  FUN_0043f6d6(*puVar5,*puVar6,0x13,0xb2,0);
  FUN_0043ded4(*puVar5,0x10000);
  FUN_0043dfa4(*puVar5,0x10);
  puVar6 = DAT_004fd8d8;
  uVar10 = FUN_00499416(*puVar3);
  *puVar6 = uVar10;
  FUN_0043f506(*puVar6,100);
  FUN_0043f568(*puVar6,0x3fffffff);
  FUN_0043f6d6(*puVar6,*puVar5,0x13,8,0xfffffffe);
  health_lock_storage();
  fVar2 = DAT_004fd5b4;
  if (*(float *)(iVar13 + 0x6c) < DAT_004fd5b4) {
    if (*(float *)(iVar13 + 0x6c) <= 0.0) {
      FUN_004b4728(auStack_70,&DAT_004fd5c8);
    }
    else {
      FUN_004b4728(auStack_70,DAT_004fd8e0,
                   (uint)(0.0 < *(float *)(iVar13 + 0x6c)) * (int)*(float *)(iVar13 + 0x6c));
    }
  }
  else {
    FUN_004b4728(auStack_70,DAT_004fd8dc);
  }
  FUN_0049942e(*puVar6,auStack_70);
  health_unlock_storage();
  uVar10 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar6,uVar10,0);
  FUN_0044143e(*puVar6,*puVar4,0);
  puVar5 = DAT_004fd8e4;
  uVar10 = FUN_00499416(*puVar3);
  *puVar5 = uVar10;
  FUN_0043f506(*puVar5,0x6e);
  FUN_0043f568(*puVar5,0x3fffffff);
  FUN_0043f6d6(*puVar5,*puVar6,0xd,0,4);
  health_lock_storage();
  uVar10 = DAT_004fd8c4;
  if (*(float *)(iVar13 + 0x70) < fVar2) {
    if (*(float *)(iVar13 + 0x70) <= 0.0) {
      uVar11 = FUN_00460084(DAT_004fd8c4);
      uVar10 = FUN_0045fffe(uVar10,uVar11);
      FUN_004b4728(auStack_70,DAT_004fd8f0,uVar10);
    }
    else {
      uVar11 = FUN_00460084(DAT_004fd8c4);
      uVar10 = FUN_0045fffe(uVar10,uVar11);
      FUN_004b4728(auStack_70,DAT_004fd8ec,uVar10,
                   (uint)(0.0 < *(float *)(iVar13 + 0x70)) * (int)*(float *)(iVar13 + 0x70));
    }
  }
  else {
    uVar11 = FUN_00460084(DAT_004fd8c4);
    uVar10 = FUN_0045fffe(uVar10,uVar11);
    FUN_004b4728(auStack_70,DAT_004fd8e8,uVar10);
  }
  FUN_0049942e(*puVar5,auStack_70);
  health_unlock_storage();
  uVar10 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar5,uVar10,0);
  FUN_0044143e(*puVar5,*puVar4,0);
  health_lock_storage();
  uVar17 = *(uint *)(iVar13 + 0xc4);
  health_unlock_storage();
  puVar5 = DAT_004fd900;
  if (uVar17 == 0) {
    uVar10 = FUN_00499416(puVar3[1]);
    *puVar5 = uVar10;
    FUN_0043f506(*puVar5,0x218);
    FUN_0043f568(*puVar5,0x3fffffff);
    FUN_0043f6b8(*puVar5,9,0,0);
    uVar10 = DAT_004fd904;
    uVar11 = FUN_00460084(DAT_004fd904);
    uVar10 = FUN_0045fffe(uVar10,uVar11);
    FUN_0049942e(*puVar5,uVar10);
    uVar10 = FUN_0044104c(0xffffff);
    FUN_0044140e(*puVar5,uVar10,0);
    FUN_0044143e(*puVar5,*puVar4,0);
    FUN_0044145a(*puVar5,2,0);
  }
  else {
    iVar16 = 0;
    for (uVar14 = 0; uVar14 < uVar17; uVar14 = uVar14 + 1) {
      health_lock_storage();
      bVar1 = *(byte *)(uVar14 * 0x101 + iVar13 + 200);
      health_unlock_storage();
      iVar8 = DAT_004fd8f4;
      iVar15 = DAT_004fd78c;
      if ((bVar1 != 2) &&
         ((bVar1 < 2 ||
          ((((iVar15 = DAT_004fd88c, bVar1 != 4 && (iVar15 = DAT_004fd78c, 3 < bVar1)) &&
            (iVar15 = DAT_004fd8d4, bVar1 != 6)) &&
           (((iVar15 = DAT_004fd8f8, 5 < bVar1 && (iVar15 = DAT_004fd8b0, bVar1 != 8)) &&
            (iVar15 = DAT_004fd8fc, 7 < bVar1)))))))) {
        iVar15 = 0;
      }
      if (iVar15 != 0) {
        uVar10 = FUN_00499416(puVar3[1]);
        *(undefined4 *)(iVar8 + iVar16 * 8 + 4) = uVar10;
        FUN_0043f506(*(undefined4 *)(iVar8 + iVar16 * 8 + 4),0x1f8);
        FUN_0043f568(*(undefined4 *)(iVar8 + iVar16 * 8 + 4),0x3fffffff);
        if (iVar16 == 0) {
          FUN_0043f6b8(*(undefined4 *)(iVar8 + 4),1,0x20,0);
        }
        else {
          FUN_0043f6d6(*(undefined4 *)(iVar8 + iVar16 * 8 + 4),
                       *(undefined4 *)(iVar8 + iVar16 * 8 + -4),0xd,0,0x18);
        }
        uVar10 = FUN_0044104c(0xffffff);
        FUN_0044140e(*(undefined4 *)(iVar8 + iVar16 * 8 + 4),uVar10,0);
        FUN_0044143e(*(undefined4 *)(iVar8 + iVar16 * 8 + 4),*puVar4,0);
        health_lock_storage();
        FUN_0049942e(*(undefined4 *)(iVar8 + iVar16 * 8 + 4),uVar14 * 0x101 + iVar13 + 0xc9);
        health_unlock_storage();
        uVar10 = FUN_00498668(puVar3[1]);
        *(undefined4 *)(iVar8 + iVar16 * 8) = uVar10;
        FUN_00498680(*(undefined4 *)(iVar8 + iVar16 * 8),iVar15);
        FUN_0043f506(*(undefined4 *)(iVar8 + iVar16 * 8),0x18);
        FUN_0043f568(*(undefined4 *)(iVar8 + iVar16 * 8),0x18);
        FUN_0043f6d6(*(undefined4 *)(iVar8 + iVar16 * 8),*(undefined4 *)(iVar8 + iVar16 * 8 + 4),
                     0x10,0xfffffff8,2);
        FUN_0043ded4(*(undefined4 *)(iVar8 + iVar16 * 8),0x10000);
        FUN_0043dfa4(*(undefined4 *)(iVar8 + iVar16 * 8),0x10);
        iVar16 = iVar16 + 1;
      }
    }
  }
  puVar3 = DAT_004fd908;
  uVar10 = FUN_0043de82(param_1);
  *puVar3 = uVar10;
  FUN_0043f506(*puVar3,0x3fffffff);
  FUN_0043f568(*puVar3,0x3fffffff);
  FUN_0043f6b8(*puVar3,8,0xfffffff8,0);
  uVar10 = FUN_0044104c(0);
  FUN_0044127e(*puVar3,uVar10,0);
  FUN_0044129e(*puVar3,0xff,0);
  FUN_0044131c(*puVar3,0,0);
  FUN_0044146a(*puVar3,0,0);
  FUN_004fb1c0(*puVar3,0,0);
  FUN_0044e368(*puVar3,0);
  FUN_0043ded4(*puVar3,0x10000);
  FUN_0043dfa4(*puVar3,0x12);
  for (iVar13 = 0; piVar9 = DAT_004fd910, puVar4 = DAT_004fd90c, iVar13 < 2; iVar13 = iVar13 + 1) {
    uVar10 = FUN_0043de82(*puVar3);
    puVar4[iVar13] = uVar10;
    FUN_0043f506(puVar4[iVar13],4);
    FUN_0043f568(puVar4[iVar13],4);
    if (iVar13 == 0) {
      FUN_0043f6b8(*puVar4,1,0,0);
    }
    else {
      FUN_0043f6d6(puVar4[iVar13],puVar4[iVar13 + -1],0xd,0,8);
    }
    uVar10 = FUN_0044104c(0xffffff);
    FUN_0044127e(puVar4[iVar13],uVar10,0);
    FUN_0044129e(puVar4[iVar13],0xff,0);
    FUN_0044131c(puVar4[iVar13],0,0);
    FUN_0044146a(puVar4[iVar13],0,0);
    FUN_004fb1c0(puVar4[iVar13],0,0);
    FUN_0043dfa4(puVar4[iVar13],0x12);
  }
  FUN_004fb1fa(*DAT_004fd910);
  FUN_0044ea04(*DAT_004fd914,*piVar9 << 8,0);
  return (ulonglong)param_1 << 0x20;
}

