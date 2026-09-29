
undefined4 FUN_004fac74(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  short *psVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 uVar6;
  
  bVar1 = false;
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004fb13c,DAT_004fb07c,DAT_004fb158,0x11d5,DAT_004fb154,*DAT_004fb150,
                 *DAT_004fb14c,param_4);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_004fb15c,DAT_004fb15c,*DAT_004fb150,*DAT_004fb14c);
  }
  psVar2 = DAT_004fb150;
  if ((*DAT_004fb150 == 0) || (*DAT_004fb14c == '\0')) {
    FUN_004f5596();
    *DAT_004fb160 = 0xffffffff;
    bVar1 = true;
  }
  else if (*DAT_004fb14c != '\0') {
    if (3 < *(byte *)(DAT_004fb150 + 0x1727) - 1) {
      return 0xffffffff;
    }
    bVar1 = false;
  }
  puVar3 = DAT_004fb164;
  if (bVar1) {
    uVar6 = FUN_0043de82(param_1);
    *puVar3 = uVar6;
    FUN_0043f4c0(*puVar3,0x240,0x120);
    FUN_0043f09a(*puVar3,0xffffffff,0xffffffff);
    uVar6 = FUN_0044104c(0);
    FUN_0044127e(*puVar3,uVar6,0);
    FUN_0044129e(*puVar3,0xff,0);
    uVar6 = FUN_0044104c(0xffffff);
    FUN_004412ec(*puVar3,uVar6,0);
    FUN_0044131c(*puVar3,0,0);
    FUN_004f5068(*puVar3,0,0);
    FUN_0044146a(*puVar3,0,0);
    FUN_0043dfa4(*puVar3,0x10);
    puVar4 = DAT_004fb168;
    uVar6 = FUN_0043de82(*puVar3);
    *puVar4 = uVar6;
    FUN_0043f4c0(*puVar4,0x240,0x110);
    FUN_0043f09a(*puVar4,0,8);
    FUN_0044120e(*puVar4,0,0);
    FUN_0044121c(*puVar4,0,0);
    FUN_0044122a(*puVar4,0xc,0);
    FUN_00441238(*puVar4,0x12,0);
    uVar6 = FUN_0044104c(0xffffff);
    FUN_004412ec(*puVar4,uVar6,0);
    FUN_0044131c(*puVar4,0,0);
    uVar6 = FUN_0044104c(0);
    FUN_0044127e(*puVar4,uVar6,0);
    FUN_0044129e(*puVar4,0xff,0);
    FUN_0044146a(*puVar4,0,0);
    FUN_0043ded4(*puVar4,0x10);
    FUN_0044e3ca(*puVar4,0xc);
    FUN_0044e368(*puVar4,3);
    uVar6 = FUN_0044104c(0xffffff);
    FUN_0044127e(*puVar4,uVar6,0x10000);
    FUN_0044129e(*puVar4,0,0x10000);
    FUN_00441164(*puVar4,2,0x10000);
    puVar4 = DAT_004fb16c;
    uVar6 = FUN_0043de82(*puVar3);
    *puVar4 = uVar6;
    FUN_0043f4c0(*puVar4,0x240,0x120);
    FUN_0043f09a(*puVar4,0,0);
    uVar6 = FUN_0044104c(0);
    FUN_0044127e(*puVar4,uVar6,0);
    FUN_0044129e(*puVar4,0,0);
    FUN_0044146a(*puVar4,6,0);
    FUN_004f5068(*puVar4,0,0);
    FUN_0044e368(*puVar4,0);
    uVar6 = FUN_0044104c(0xffffff);
    FUN_004412ec(*puVar4,uVar6,0);
    FUN_0044131c(*puVar4,1,0);
    FUN_0043dfa4(*puVar4,1);
    FUN_004f9484();
    if ((*psVar2 != 0) && (*DAT_004fb14c == '\0')) {
      FUN_0043f66c(*puVar3);
      FUN_004f7ae4(0);
    }
  }
  else {
    FUN_004fab18();
  }
  return 0;
}

