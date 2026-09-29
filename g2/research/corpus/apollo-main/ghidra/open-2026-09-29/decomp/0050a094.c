
undefined4 FUN_0050a094(void)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  int iVar7;
  undefined4 uVar8;
  undefined4 in_r3;
  
  iVar7 = DAT_0050aaf8;
  piVar1 = DAT_0050aaf4;
  if ((*DAT_0050aaf0 == 0) || (*DAT_0050aaf4 < 0)) {
    uVar6 = 0;
  }
  else {
    if (*(int *)(DAT_0050aaf8 + *DAT_0050aaf4 * 8 + 4) != 0) {
      FUN_0044d878(*(undefined4 *)(DAT_0050aaf8 + *DAT_0050aaf4 * 8 + 4));
    }
    if (*(int *)(iVar7 + *piVar1 * 8 + 4) == 0) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0050ac28,DAT_0050ac24,DAT_0050ac20,0xd5,DAT_0050ac1c,*piVar1,*piVar1 + 1,
                     in_r3);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_0050ac2c,DAT_0050ac2c,*piVar1,*piVar1 + 1);
      }
      uVar6 = 0xffffffff;
    }
    else {
      FUN_0043c0e4(DAT_0050ac30,0xc88,0);
      puVar2 = DAT_0050ac34;
      uVar6 = FUN_0043de82(*(undefined4 *)(iVar7 + *piVar1 * 8 + 4));
      *puVar2 = uVar6;
      FUN_0043f09a(*puVar2,0x14,0x10);
      FUN_0043f506(*puVar2,0x13b);
      FUN_0043f568(*puVar2,0x100);
      uVar6 = FUN_0044104c(0);
      FUN_0044127e(*puVar2,uVar6,0);
      FUN_0044129e(*puVar2,0,0);
      FUN_0044131c(*puVar2,0,0);
      FUN_0044133a(*puVar2,0,0);
      FUN_00441378(*puVar2,0,0);
      FUN_00441386(*puVar2,0,0);
      FUN_004413b0(*puVar2,0,0);
      FUN_00441394(*puVar2,0,0);
      FUN_004413a2(*puVar2,0,0);
      FUN_00509fdc(*puVar2,0,0);
      FUN_0044120e(*puVar2,0,0);
      FUN_0044121c(*puVar2,0,0);
      FUN_0044122a(*puVar2,0,0);
      FUN_00441238(*puVar2,0,0);
      FUN_0044146a(*puVar2,0,0);
      uVar6 = FUN_0044104c(0);
      FUN_004412ec(*puVar2,uVar6,0);
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(*puVar2,uVar6,0);
      FUN_0044142e(*puVar2,0xff,0);
      FUN_0043dfa4(*puVar2,0x10);
      puVar3 = DAT_0050ac38;
      uVar6 = FUN_00498668(*puVar2);
      *puVar3 = uVar6;
      FUN_00498680(*puVar3,DAT_0050ac3c);
      FUN_0043f506(*puVar3,0x18);
      FUN_0043f568(*puVar3,0x18);
      FUN_0043f0e0(*puVar3,0);
      FUN_0043f142(*puVar3,2);
      FUN_0043ded4(*puVar3,0x10000);
      FUN_0043dfa4(*puVar3,0x10);
      puVar3 = DAT_0050ac40;
      uVar6 = FUN_00499416(*puVar2);
      *puVar3 = uVar6;
      FUN_0043f506(*puVar3,0xda);
      FUN_0043f568(*puVar3,0x1c);
      FUN_0043f0e0(*puVar3,0x20);
      FUN_0043f142(*puVar3,0);
      FUN_00499678(*puVar3,1);
      uVar6 = DAT_0050ac44;
      uVar8 = FUN_00460084(DAT_0050ac44);
      uVar6 = FUN_0045fffe(uVar6,uVar8);
      FUN_0049942e(*puVar3,uVar6);
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(*puVar3,uVar6,0);
      puVar4 = DAT_0050ac48;
      FUN_0044143e(*puVar3,*DAT_0050ac48,0);
      puVar3 = DAT_0050ac4c;
      uVar6 = FUN_00499416(*puVar2);
      *puVar3 = uVar6;
      FUN_0043f506(*puVar3,0x3c);
      FUN_0043f568(*puVar3,0x1c);
      FUN_0043f0e0(*puVar3,0xfa);
      FUN_0043f142(*puVar3,0);
      FUN_00499678(*puVar3,1);
      FUN_0049942e(*puVar3,DAT_0050ac50);
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(*puVar3,uVar6,0);
      FUN_0044143e(*puVar3,*puVar4,0);
      puVar3 = DAT_0050ac54;
      uVar6 = FUN_00499416(*puVar2);
      *puVar3 = uVar6;
      FUN_0043f506(*puVar3,0x13b);
      FUN_0043f568(*puVar3,0x3fffffff);
      FUN_0043f0e0(*puVar3,0);
      FUN_0043f142(*puVar3,0x38);
      FUN_00499678(*puVar3,1);
      uVar6 = DAT_0050ac58;
      uVar8 = FUN_00460084(DAT_0050ac58);
      uVar6 = FUN_0045fffe(uVar6,uVar8);
      FUN_0049942e(*puVar3,uVar6);
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(*puVar3,uVar6,0);
      FUN_0044143e(*puVar3,*puVar4,0);
      puVar5 = DAT_0050af48;
      uVar6 = FUN_00499416(*puVar2);
      *puVar5 = uVar6;
      FUN_0043f506(*puVar5,0x13b);
      FUN_0043f568(*puVar5,0x96);
      FUN_0043f0e0(*puVar5,0);
      FUN_0043f6d6(*puVar5,*puVar3,0xe,0,0x1c);
      FUN_00499678(*puVar5,1);
      uVar6 = DAT_0050afa0;
      uVar8 = FUN_00460084(DAT_0050afa0);
      uVar6 = FUN_0045fffe(uVar6,uVar8);
      FUN_0049942e(*puVar5,uVar6);
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(*puVar5,uVar6,0);
      uVar6 = FUN_0044143e(*puVar5,*puVar4,0);
    }
  }
  return uVar6;
}

