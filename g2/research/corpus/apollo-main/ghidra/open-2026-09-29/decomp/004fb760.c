
longlong FUN_004fb760(int param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  float fVar1;
  int *piVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  uint uVar10;
  uint in_fpscr;
  int iVar11;
  uint uVar12;
  float fVar13;
  float fVar14;
  uint local_54;
  undefined1 auStack_50 [32];
  
  *DAT_004fc1c4 = 1;
  piVar2 = DAT_004fc1d4;
  *DAT_004fc1d4 = param_1;
  FUN_0043c0e4(DAT_004fba30,auStack_50,0x20,0);
  puVar3 = DAT_004fc344;
  uVar8 = FUN_0043de82(*(undefined4 *)(DAT_004fc1d8 + *piVar2 * 8 + 4));
  *puVar3 = uVar8;
  FUN_0043f09a(*puVar3,0x14,0x10);
  FUN_0043f506(*puVar3,0x13b);
  FUN_0043f568(*puVar3,0x100);
  uVar8 = FUN_0044104c(0);
  FUN_0044127e(*puVar3,uVar8,0);
  FUN_0044129e(*puVar3,0,0);
  FUN_0044131c(*puVar3,0,0);
  FUN_0044133a(*puVar3,0,0);
  FUN_00441378(*puVar3,0,0);
  FUN_00441386(*puVar3,0,0);
  FUN_004413b0(*puVar3,0,0);
  FUN_00441394(*puVar3,0,0);
  FUN_004413a2(*puVar3,0,0);
  FUN_004fb1c0(*puVar3,0,0);
  FUN_0044120e(*puVar3,0,0);
  FUN_0044121c(*puVar3,0,0);
  FUN_0044122a(*puVar3,0,0);
  FUN_00441238(*puVar3,0,0);
  FUN_0044146a(*puVar3,0,0);
  uVar8 = FUN_0044104c(0);
  FUN_004412ec(*puVar3,uVar8,0);
  uVar8 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar3,uVar8,0);
  FUN_0044142e(*puVar3,0xff,0);
  FUN_0043dfa4(*puVar3,0x10);
  FUN_0044e368(*puVar3,0);
  puVar4 = DAT_004fc348;
  uVar8 = FUN_00498668(*puVar3);
  *puVar4 = uVar8;
  health_lock_storage();
  iVar5 = DAT_004fc34c;
  if (*(char *)(DAT_004fc34c + 0xc0) == '\x01') {
    FUN_00498680(*puVar4,DAT_004fc350);
  }
  else if (*(char *)(DAT_004fc34c + 0xc0) == '\x03') {
    FUN_00498680(*puVar4,DAT_004fc354);
  }
  else {
    FUN_00498680(*puVar4,DAT_004fc358);
  }
  health_unlock_storage();
  FUN_0043f506(*puVar4,0x18);
  FUN_0043f568(*puVar4,0x18);
  FUN_0043f0e0(*puVar4,0);
  FUN_0043f142(*puVar4,2);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar6 = DAT_004fc35c;
  uVar8 = FUN_00499416(*puVar3);
  *puVar6 = uVar8;
  FUN_0043f506(*puVar6,0x3fffffff);
  FUN_0043f568(*puVar6,0x3fffffff);
  FUN_0043f6d6(*puVar6,*puVar4,0x13,8,0xfffffffe);
  uVar8 = DAT_004fc580;
  uVar9 = FUN_00460084(DAT_004fc580);
  uVar8 = FUN_0045fffe(uVar8,uVar9);
  FUN_0049942e(*puVar6,uVar8);
  uVar8 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar6,uVar8,0);
  FUN_0044143e(*puVar6,*DAT_004fc584,0);
  health_lock_storage();
  iVar11 = (uint)(0.0 < *(float *)(iVar5 + 0xb4)) * (int)*(float *)(iVar5 + 0xb4);
  health_unlock_storage();
  if (iVar11 == 0) {
    FUN_004b4728(auStack_50,&DAT_004fbc90);
  }
  else {
    FUN_004b4728(auStack_50,&DAT_004fbc8c,iVar11);
  }
  puVar4 = DAT_004fc588;
  uVar8 = FUN_00499416(*puVar3);
  *puVar4 = uVar8;
  FUN_0043f506(*puVar4,0x3fffffff);
  FUN_0043f568(*puVar4,0x3fffffff);
  FUN_0043f6b8(*puVar4,3,0,0);
  FUN_0049942e(*puVar4,auStack_50);
  uVar8 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar4,uVar8,0);
  FUN_0044143e(*puVar4,*DAT_004fc584,0);
  health_lock_storage();
  uVar12 = (uint)(0.0 < *(float *)(iVar5 + 0xc)) * (int)*(float *)(iVar5 + 0xc);
  if (*(int *)(iVar5 + 8) == 0) {
    uVar10 = 10000;
  }
  else {
    uVar10 = *(uint *)(iVar5 + 8);
  }
  health_unlock_storage();
  puVar4 = DAT_004fc58c;
  uVar8 = FUN_00498668(*puVar3);
  *puVar4 = uVar8;
  FUN_00498680(*puVar4,DAT_004fc590);
  FUN_0043f506(*puVar4,0x18);
  FUN_0043f568(*puVar4,0x18);
  FUN_0043f0e0(*puVar4,0);
  FUN_0043f142(*puVar4,0x37);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar6 = DAT_004fc594;
  uVar8 = FUN_00499416(*puVar3);
  *puVar6 = uVar8;
  FUN_0043f506(*puVar6,0x13b);
  FUN_0043f568(*puVar6,0x3fffffff);
  FUN_0043f6d6(*puVar6,*puVar4,0x13,8,0xfffffffe);
  uVar8 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar6,uVar8,0);
  FUN_0044143e(*puVar6,*DAT_004fc584,0);
  if (uVar12 == 0) {
    uVar8 = FUN_00460084(DAT_004fc598);
    uVar8 = FUN_0045fffe(DAT_004fc598,uVar8);
    FUN_004b4728(auStack_50,DAT_004fc5a0,uVar8);
  }
  else {
    uVar8 = FUN_00460084(DAT_004fc598);
    uVar8 = FUN_0045fffe(DAT_004fc598,uVar8);
    FUN_004b4728(auStack_50,DAT_004fc59c,uVar8,uVar12);
  }
  FUN_0049942e(*puVar6,auStack_50);
  puVar6 = DAT_004fc5a4;
  uVar8 = FUN_00498668(*puVar3);
  *puVar6 = uVar8;
  FUN_00498680(*puVar6,DAT_004fc5a8);
  FUN_0043f506(*puVar6,0x138);
  FUN_0043f568(*puVar6,8);
  FUN_0043f6d6(*puVar6,*puVar4,0xd,0,10);
  FUN_0043ded4(*puVar6,0x10000);
  FUN_0043dfa4(*puVar6,0x10);
  puVar4 = DAT_004fc5ac;
  fVar1 = DAT_004fbe0c;
  fVar13 = DAT_004fbe08;
  if (uVar12 != 0) {
    if (uVar12 < uVar10) {
      fVar13 = (float)VectorUnsignedToFloat(uVar12,(byte)(in_fpscr >> 0x16) & 3);
      fVar14 = (float)VectorUnsignedToFloat(uVar10,(byte)(in_fpscr >> 0x16) & 3);
      fVar13 = fVar13 / fVar14;
    }
    else {
      fVar13 = 1.0;
    }
  }
  iVar11 = ((int)(fVar13 * DAT_004fbe0c + 1.0) / 3) * 3;
  if (0x138 < iVar11) {
    iVar11 = 0x138;
  }
  uVar8 = FUN_0043de82(*puVar3);
  *puVar4 = uVar8;
  FUN_0043f506(*puVar4,0x138 - iVar11);
  FUN_0043f568(*puVar4,8);
  FUN_0043f6d6(*puVar4,*puVar6,1,iVar11,0);
  uVar8 = FUN_0044104c(0);
  FUN_0044127e(*puVar4,uVar8,0);
  FUN_0044129e(*puVar4,0xbe,0);
  FUN_004fb1c0(*puVar4,0,0);
  FUN_0044131c(*puVar4,0,0);
  FUN_0044146a(*puVar4,0,0);
  FUN_0043dfa4(*puVar4,0x10);
  health_lock_storage();
  uVar12 = (uint)(0.0 < *(float *)(iVar5 + 0x24)) * (int)*(float *)(iVar5 + 0x24);
  if (*(int *)(iVar5 + 0x20) == 0) {
    local_54 = 2000;
  }
  else {
    local_54 = *(uint *)(iVar5 + 0x20);
  }
  health_unlock_storage();
  puVar6 = DAT_004fc5b0;
  uVar8 = FUN_00498668(*puVar3);
  *puVar6 = uVar8;
  FUN_00498680(*puVar6,DAT_004fc5b4);
  FUN_0043f506(*puVar6,0x18);
  FUN_0043f568(*puVar6,0x18);
  FUN_0043f0e0(*puVar6,0);
  FUN_0043f142(*puVar6,0x75);
  FUN_0043ded4(*puVar6,0x10000);
  FUN_0043dfa4(*puVar6,0x10);
  puVar7 = DAT_004fc5b8;
  uVar8 = FUN_00499416(*puVar3);
  *puVar7 = uVar8;
  FUN_0043f506(*puVar7,0x13b);
  FUN_0043f568(*puVar7,0x3fffffff);
  FUN_0043f6d6(*puVar7,*puVar6,0x13,8,0xfffffffe);
  uVar8 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar7,uVar8,0);
  puVar4 = DAT_004fc584;
  FUN_0044143e(*puVar7,*DAT_004fc584,0);
  if (uVar12 == 0) {
    uVar8 = FUN_00460084(DAT_004fc5bc);
    uVar8 = FUN_0045fffe(DAT_004fc5bc,uVar8);
    FUN_004b4728(auStack_50,DAT_004fc5a0,uVar8);
  }
  else {
    uVar8 = FUN_00460084(DAT_004fc5bc);
    uVar8 = FUN_0045fffe(DAT_004fc5bc,uVar8);
    FUN_004b4728(auStack_50,DAT_004fc59c,uVar8,uVar12);
  }
  FUN_0049942e(*puVar7,auStack_50);
  puVar7 = DAT_004fc5c0;
  uVar8 = FUN_00498668(*puVar3);
  *puVar7 = uVar8;
  FUN_00498680(*puVar7,DAT_004fc5a8);
  FUN_0043f506(*puVar7,0x138);
  FUN_0043f568(*puVar7,8);
  FUN_0043f6d6(*puVar7,*puVar6,0xd,0,10);
  FUN_0043ded4(*puVar7,0x10000);
  FUN_0043dfa4(*puVar7,0x10);
  puVar6 = DAT_004fc5c4;
  fVar13 = DAT_004fbe08;
  if (uVar12 != 0) {
    if (uVar12 < local_54) {
      fVar13 = (float)VectorUnsignedToFloat(uVar12,(byte)(in_fpscr >> 0x16) & 3);
      fVar14 = (float)VectorUnsignedToFloat(local_54,(byte)(in_fpscr >> 0x16) & 3);
      fVar13 = fVar13 / fVar14;
    }
    else {
      fVar13 = 1.0;
    }
  }
  iVar11 = ((int)(fVar13 * fVar1 + 1.0) / 3) * 3;
  if (0x138 < iVar11) {
    iVar11 = 0x138;
  }
  uVar8 = FUN_0043de82(*puVar3);
  *puVar6 = uVar8;
  FUN_0043f506(*puVar6,0x138 - iVar11);
  FUN_0043f568(*puVar6,8);
  FUN_0043f6d6(*puVar6,*puVar7,1,iVar11,0);
  uVar8 = FUN_0044104c(0);
  FUN_0044127e(*puVar6,uVar8,0);
  FUN_0044129e(*puVar6,0xbe,0);
  FUN_004fb1c0(*puVar6,0,0);
  FUN_0044131c(*puVar6,0,0);
  FUN_0044146a(*puVar6,0,0);
  FUN_0043dfa4(*puVar6,0x10);
  puVar6 = DAT_004fc5c8;
  uVar8 = FUN_00498668(*puVar3);
  *puVar6 = uVar8;
  FUN_00498680(*puVar6,DAT_004fc5cc);
  FUN_0043f506(*puVar6,0x18);
  FUN_0043f568(*puVar6,0x18);
  FUN_0043f0e0(*puVar6,0);
  FUN_0043f142(*puVar6,0xbc);
  FUN_0043ded4(*puVar6,0x10000);
  FUN_0043dfa4(*puVar6,0x10);
  puVar7 = DAT_004fc5d0;
  uVar8 = FUN_00499416(*puVar3);
  *puVar7 = uVar8;
  FUN_0043f506(*puVar7,0x82);
  FUN_0043f568(*puVar7,0x3fffffff);
  FUN_0043f6d6(*puVar7,*puVar6,0xd,0,6);
  health_lock_storage();
  if (*(float *)(iVar5 + 0x3c) <= 0.0) {
    FUN_004b4728(auStack_50,&DAT_004fc1bc);
  }
  else {
    FUN_004b4728(auStack_50,&DAT_004fc1b8,
                 (uint)(0.0 < *(float *)(iVar5 + 0x3c)) * (int)*(float *)(iVar5 + 0x3c));
  }
  FUN_0049942e(*puVar7,auStack_50);
  health_unlock_storage();
  FUN_0044143e(*puVar7,*puVar4,0);
  uVar8 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar7,uVar8,0);
  puVar7 = DAT_004fc5d4;
  uVar8 = FUN_00498668(*puVar3);
  *puVar7 = uVar8;
  FUN_00498680(*puVar7,DAT_004fc5d8);
  FUN_0043f506(*puVar7,0x18);
  FUN_0043f568(*puVar7,0x18);
  FUN_0043f6d6(*puVar7,*puVar6,0x13,0x6b,0);
  FUN_0043ded4(*puVar7,0x10000);
  FUN_0043dfa4(*puVar7,0x10);
  puVar6 = DAT_004fc5dc;
  uVar8 = FUN_00499416(*puVar3);
  *puVar6 = uVar8;
  FUN_0043f506(*puVar6,0x7b);
  FUN_0043f568(*puVar6,0x3fffffff);
  FUN_0043f6d6(*puVar6,*puVar7,0xd,0,6);
  health_lock_storage();
  uVar8 = DAT_004fc5e0;
  if (*(float *)(iVar5 + 0x54) <= 0.0) {
    uVar9 = FUN_00460084(DAT_004fc5e0);
    uVar8 = FUN_0045fffe(uVar8,uVar9);
    FUN_004b4728(auStack_50,&DAT_004fc330,uVar8);
  }
  else {
    uVar9 = FUN_00460084(DAT_004fc5e0);
    uVar8 = FUN_0045fffe(uVar8,uVar9);
    FUN_004b4728(auStack_50,DAT_004fc5e4,
                 (uint)(0.0 < *(float *)(iVar5 + 0x54)) * (int)*(float *)(iVar5 + 0x54),uVar8);
  }
  FUN_0049942e(*puVar6,auStack_50);
  health_unlock_storage();
  uVar8 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar6,uVar8,0);
  FUN_0044143e(*puVar6,*puVar4,0);
  puVar6 = DAT_004fc5e8;
  uVar8 = FUN_00498668(*puVar3);
  *puVar6 = uVar8;
  FUN_00498680(*puVar6,DAT_004fc5ec);
  FUN_0043f506(*puVar6,0x18);
  FUN_0043f568(*puVar6,0x18);
  FUN_0043f6d6(*puVar6,*puVar7,0x13,0x6b,0);
  FUN_0043ded4(*puVar6,0x10000);
  FUN_0043dfa4(*puVar6,0x10);
  puVar7 = DAT_004fc5f0;
  uVar8 = FUN_00499416(*puVar3);
  *puVar7 = uVar8;
  FUN_0043f506(*puVar7,0x35);
  FUN_0043f568(*puVar7,0x3fffffff);
  FUN_0043f6d6(*puVar7,*puVar6,0xd,0,6);
  health_lock_storage();
  if (*(float *)(iVar5 + 0x6c) < DAT_004fc334) {
    if (*(float *)(iVar5 + 0x6c) <= 0.0) {
      FUN_004b4728(auStack_50,&DAT_004fc338);
    }
    else {
      FUN_004b4728(auStack_50,DAT_004fc5f8,
                   (uint)(0.0 < *(float *)(iVar5 + 0x6c)) * (int)*(float *)(iVar5 + 0x6c));
    }
  }
  else {
    FUN_004b4728(auStack_50,DAT_004fc5f4);
  }
  FUN_0049942e(*puVar7,auStack_50);
  health_unlock_storage();
  uVar8 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar7,uVar8,0);
  FUN_0044143e(*puVar7,*puVar4,0);
  return (ulonglong)param_4 << 0x20;
}

