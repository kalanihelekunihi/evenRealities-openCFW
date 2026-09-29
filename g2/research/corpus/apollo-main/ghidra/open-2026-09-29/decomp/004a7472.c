
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void hub_calibration_display_update(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  
  puVar1 = _DAT_004a7750;
  uVar4 = FUN_0043de82();
  *puVar1 = uVar4;
  FUN_0043f4c0(*puVar1,0x240,0x120);
  FUN_0043f09a(*puVar1,0,0);
  FUN_0043dfa4(*puVar1,0x10);
  uVar4 = FUN_0044104c(0);
  FUN_0044127e(*puVar1,uVar4,0);
  FUN_0044129e(*puVar1,0xff,0);
  FUN_0044131c(*puVar1,0,0);
  FUN_0044146a(*puVar1,0,0);
  hub_calibration_labels_update(*puVar1,0,0);
  puVar2 = _DAT_004a7754;
  uVar4 = FUN_00499416(*puVar1);
  *puVar2 = uVar4;
  FUN_0043f4c0(*puVar2,300,0x1c);
  FUN_0043f09a(*puVar2,0x8a,99);
  FUN_0044145a(*puVar2,2,0);
  uVar4 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar2,uVar4,0);
  puVar3 = _DAT_004a7758;
  FUN_0044143e(*puVar2,*_DAT_004a7758,0);
  FUN_0044129e(*puVar2,0,0);
  FUN_0044131c(*puVar2,0,0);
  uVar4 = _DAT_004a775c;
  uVar5 = FUN_00460084(_DAT_004a775c);
  uVar4 = FUN_0045fffe(uVar4,uVar5);
  FUN_0049942e(*puVar2,uVar4);
  puVar2 = _DAT_004a7760;
  uVar4 = FUN_00499416(*puVar1);
  *puVar2 = uVar4;
  FUN_0043f568(*puVar2,0x1c);
  FUN_0044145a(*puVar2,2,0);
  uVar4 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar2,uVar4,0);
  FUN_0044143e(*puVar2,*puVar3,0);
  FUN_0044129e(*puVar2,0,0);
  FUN_0044131c(*puVar2,0,0);
  uVar4 = _DAT_004a7764;
  uVar5 = FUN_00460084(_DAT_004a7764);
  uVar4 = FUN_0045fffe(uVar4,uVar5);
  FUN_0049942e(*puVar2,uVar4);
  FUN_0043f506(*puVar2,0x3fffffff);
  FUN_0043f66c(*puVar2);
  iVar6 = FUN_0043fd9e(*puVar2);
  FUN_0043f09a(*puVar2,(0x240 - iVar6) / 2,0xa1);
  puVar2 = _DAT_004a7768;
  uVar4 = FUN_0043de82(*puVar1);
  *puVar2 = uVar4;
  FUN_0043f506(*puVar2,0xf0);
  FUN_0043f568(*puVar2,2);
  FUN_0043f0e0(*puVar2,0x27);
  FUN_0043f142(*puVar2,0x8f);
  uVar4 = FUN_0044104c(0xffffff);
  FUN_0044127e(*puVar2,uVar4,0);
  FUN_0044129e(*puVar2,0xff,0);
  FUN_0044131c(*puVar2,0,0);
  hub_calibration_labels_update(*puVar2,0,0);
  puVar2 = _DAT_004a776c;
  uVar4 = FUN_0043de82(*puVar1);
  *puVar2 = uVar4;
  FUN_0043f506(*puVar2,0xf0);
  FUN_0043f568(*puVar2,2);
  FUN_0043f0e0(*puVar2,0x129);
  FUN_0043f142(*puVar2,0x8f);
  uVar4 = FUN_0044104c(0xffffff);
  FUN_0044127e(*puVar2,uVar4,0);
  FUN_0044129e(*puVar2,0xff,0);
  FUN_0044131c(*puVar2,0,0);
  hub_calibration_labels_update(*puVar2,0,0);
  puVar2 = _DAT_004a7770;
  uVar4 = FUN_0043de82(*puVar1);
  *puVar2 = uVar4;
  FUN_0043f4c0(*puVar2,2,2);
  FUN_0043f09a(*puVar2,0x11f,0x8f);
  FUN_0044146a(*puVar2,1,0);
  uVar4 = FUN_0044104c(0xffffff);
  FUN_0044127e(*puVar2,uVar4,0);
  FUN_0044129e(*puVar2,0xff,0);
  FUN_0044131c(*puVar2,0,0);
  FUN_0043dfa4(*puVar2,0x12);
  return;
}

