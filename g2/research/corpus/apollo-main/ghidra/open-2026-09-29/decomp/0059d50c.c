
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
translate_ui_0059d50c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar6 = DAT_0059df78;
  uVar2 = FUN_0043de82();
  *(undefined4 *)(iVar6 + 0x10) = uVar2;
  uVar2 = _DAT_0059df8c;
  FUN_0043f4c0(*(undefined4 *)(iVar6 + 0x10),_DAT_0059df8c,0x3fffffff);
  FUN_004411aa(*(undefined4 *)(iVar6 + 0x10),0x70,0);
  iVar7 = -0xc;
  FUN_0043f6d6(*(undefined4 *)(iVar6 + 0x10),*(undefined4 *)(iVar6 + 0x18),0xb,0,0xfffffff4,param_2,
               param_3,param_4);
  uVar3 = FUN_0044104c(0);
  FUN_0044127e(*(undefined4 *)(iVar6 + 0x10),uVar3,0);
  FUN_0044129e(*(undefined4 *)(iVar6 + 0x10),0xff,0);
  FUN_0044131c(*(undefined4 *)(iVar6 + 0x10),0,0);
  translate_ui_0059d380(*(undefined4 *)(iVar6 + 0x10),0,0);
  FUN_0044146a(*(undefined4 *)(iVar6 + 0x10),0,0);
  FUN_0044e368(*(undefined4 *)(iVar6 + 0x10),0);
  FUN_0043dfa4(*(undefined4 *)(iVar6 + 0x10),0x20);
  FUN_0043ded4(*(undefined4 *)(iVar6 + 0x10),0x80);
  uVar3 = FUN_00499416(*(undefined4 *)(iVar6 + 0x10));
  *(undefined4 *)(iVar6 + 0x14) = uVar3;
  FUN_0043f4c0(*(undefined4 *)(iVar6 + 0x14),uVar2,0x3fffffff);
  FUN_0043f6b8(*(undefined4 *)(iVar6 + 0x14),5,0,0);
  uVar2 = FUN_0044104c(_DAT_0059df90);
  FUN_0044140e(*(undefined4 *)(iVar6 + 0x14),uVar2,0);
  piVar1 = _DAT_0059df94;
  FUN_0044143e(*(undefined4 *)(iVar6 + 0x14),*_DAT_0059df94,0);
  iVar4 = *(int *)(*piVar1 + 0xc);
  FUN_0044144c(*(undefined4 *)(iVar6 + 0x14),0x1c - iVar4,0);
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    iVar7 = 0x90;
    param_2 = _DAT_0059df98;
    FUN_0043d574(4,DAT_0059defc,DAT_0059def8,_DAT_0059df9c,0x90,_DAT_0059df98,iVar4,0x1c - iVar4);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    iVar7 = 0x1c - iVar4;
    compress_log_output(0x10800000,_DAT_0059e114,_DAT_0059e114,iVar4);
  }
  FUN_0044129e(*(undefined4 *)(iVar6 + 0x14),0,0);
  FUN_0044131c(*(undefined4 *)(iVar6 + 0x14),0,0);
  FUN_00499678(*(undefined4 *)(iVar6 + 0x14),0);
  FUN_0044145a(*(undefined4 *)(iVar6 + 0x14),1,0);
  FUN_0049942e(*(undefined4 *)(iVar6 + 0x14),0x59d8ec);
  FUN_00441488(*(undefined4 *)(iVar6 + 0x10),0,0);
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    iVar7 = 0x98;
    param_2 = _DAT_0059e118;
    FUN_0043d574(4,DAT_0059defc,DAT_0059def8,_DAT_0059df9c);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0x10000000,_DAT_0059e3b0,_DAT_0059e3b0);
  }
  return CONCAT44(param_2,iVar7);
}

