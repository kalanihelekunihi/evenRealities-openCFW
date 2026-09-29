
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 translate_ui_0059d400(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  iVar2 = DAT_0059df78;
  uVar1 = FUN_0043de82();
  *(undefined4 *)(iVar2 + 4) = uVar1;
  FUN_0043f4c0(*(undefined4 *)(iVar2 + 4),0x3fffffff,0x3fffffff);
  FUN_0043f09a(*(undefined4 *)(iVar2 + 4),0,0xa6);
  uVar1 = FUN_0044104c(0);
  FUN_0044127e(*(undefined4 *)(iVar2 + 4),uVar1,0);
  FUN_0044129e(*(undefined4 *)(iVar2 + 4),0xff,0);
  FUN_0044131c(*(undefined4 *)(iVar2 + 4),0,0);
  translate_ui_0059d380(*(undefined4 *)(iVar2 + 4),0,0);
  FUN_0044146a(*(undefined4 *)(iVar2 + 4),0,0);
  uVar1 = FUN_0058c7a0(*(undefined4 *)(iVar2 + 4),_DAT_0059df00);
  *(undefined4 *)(iVar2 + 8) = uVar1;
  FUN_0043f4c0(*(undefined4 *)(iVar2 + 8),0x3fffffff,0x3fffffff);
  FUN_0043f6b8(*(undefined4 *)(iVar2 + 8),7,0,0);
  uVar1 = FUN_00499416(*(undefined4 *)(iVar2 + 4));
  *(undefined4 *)(iVar2 + 0xc) = uVar1;
  FUN_0043f4c0(*(undefined4 *)(iVar2 + 0xc),0x3fffffff,0x3fffffff);
  uStack_18 = 0;
  FUN_0043f6d6(*(undefined4 *)(iVar2 + 0xc),*(undefined4 *)(iVar2 + 8),0x14,0x10);
  uVar1 = FUN_0044104c(0xffffff);
  FUN_0044140e(*(undefined4 *)(iVar2 + 0xc),uVar1,0);
  FUN_0044143e(*(undefined4 *)(iVar2 + 0xc),_DAT_0059df7c,0);
  FUN_0049942e(*(undefined4 *)(iVar2 + 0xc),_DAT_0059df80);
  iVar2 = FUN_0043d0ce();
  uStack_14 = param_3;
  if (iVar2 << 0x1e < 0) {
    uStack_14 = _DAT_0059df84;
    uStack_18 = 0x73;
    FUN_0043d574(4,DAT_0059defc,DAT_0059def8,_DAT_0059df88);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,_DAT_0059e240);
  }
  return CONCAT44(uStack_14,uStack_18);
}

