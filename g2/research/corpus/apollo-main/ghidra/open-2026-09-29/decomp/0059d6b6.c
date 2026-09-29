
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
translate_ui_0059d6b6(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  iVar6 = DAT_0059df78;
  uVar2 = FUN_0043de82();
  *(undefined4 *)(iVar6 + 0x18) = uVar2;
  uVar2 = _DAT_0059df8c;
  FUN_0043f4c0(*(undefined4 *)(iVar6 + 0x18),_DAT_0059df8c,0x3fffffff);
  FUN_004411aa(*(undefined4 *)(iVar6 + 0x18),0x54,0);
  FUN_0043f6b8(*(undefined4 *)(iVar6 + 0x18),5,0,0,param_1,param_2,param_3,param_4);
  uVar3 = FUN_0044104c(0);
  FUN_0044127e(*(undefined4 *)(iVar6 + 0x18),uVar3,0);
  FUN_0044129e(*(undefined4 *)(iVar6 + 0x18),0,0);
  FUN_0044131c(*(undefined4 *)(iVar6 + 0x18),0,0);
  translate_ui_0059d380(*(undefined4 *)(iVar6 + 0x18),0,0);
  FUN_0044146a(*(undefined4 *)(iVar6 + 0x18),0,0);
  FUN_0044e368(*(undefined4 *)(iVar6 + 0x18),0);
  FUN_0043dfa4(*(undefined4 *)(iVar6 + 0x18),0x20);
  FUN_0043ded4(*(undefined4 *)(iVar6 + 0x18),0x80);
  uVar3 = FUN_00499416(*(undefined4 *)(iVar6 + 0x18));
  *(undefined4 *)(iVar6 + 0x1c) = uVar3;
  FUN_0043f4c0(*(undefined4 *)(iVar6 + 0x1c),uVar2,0x3fffffff);
  FUN_0043f6b8(*(undefined4 *)(iVar6 + 0x1c),5,0,0);
  uVar2 = FUN_0044104c(0xffffff);
  FUN_0044140e(*(undefined4 *)(iVar6 + 0x1c),uVar2,0);
  piVar1 = _DAT_0059df94;
  FUN_0044143e(*(undefined4 *)(iVar6 + 0x1c),*_DAT_0059df94,0);
  iVar4 = *(int *)(*piVar1 + 0xc);
  FUN_0044144c(*(undefined4 *)(iVar6 + 0x1c),0x1c - iVar4,0);
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    param_1 = 0xb7;
    param_2 = _DAT_0059df98;
    FUN_0043d574(4,DAT_0059defc,DAT_0059def8,_DAT_0059e244,0xb7,_DAT_0059df98,iVar4,0x1c - iVar4);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    param_1 = 0x1c - iVar4;
    compress_log_output(0x10800000,_DAT_0059e114,_DAT_0059e114,iVar4);
  }
  FUN_0044129e(*(undefined4 *)(iVar6 + 0x1c),0,0);
  FUN_0044131c(*(undefined4 *)(iVar6 + 0x1c),0,0);
  FUN_00499678(*(undefined4 *)(iVar6 + 0x1c),0);
  FUN_0044145a(*(undefined4 *)(iVar6 + 0x1c),1,0);
  FUN_0049942e(*(undefined4 *)(iVar6 + 0x1c),0x59d8ec);
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    param_1 = 0xbe;
    param_2 = _DAT_0059e25c;
    FUN_0043d574(4,DAT_0059defc,DAT_0059def8,_DAT_0059e244);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0x10000000,_DAT_0059e480,_DAT_0059e480);
  }
  return CONCAT44(param_2,param_1);
}

