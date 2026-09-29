
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 translate_ui_0059d476(void)

{
  undefined4 uVar1;
  int iVar2;
  int unaff_r4;
  undefined4 uStack00000000;
  undefined4 in_stack_00000004;
  
  FUN_0043f6b8(*(undefined4 *)(unaff_r4 + 8),7);
  uVar1 = FUN_00499416(*(undefined4 *)(unaff_r4 + 4));
  *(undefined4 *)(unaff_r4 + 0xc) = uVar1;
  FUN_0043f4c0(*(undefined4 *)(unaff_r4 + 0xc));
  uStack00000000 = 0;
  FUN_0043f6d6(*(undefined4 *)(unaff_r4 + 0xc),*(undefined4 *)(unaff_r4 + 8),0x14,0x10);
  uVar1 = FUN_0044104c(0xffffff);
  FUN_0044140e(*(undefined4 *)(unaff_r4 + 0xc),uVar1,0);
  FUN_0044143e(*(undefined4 *)(unaff_r4 + 0xc),_DAT_0059df7c,0);
  FUN_0049942e(*(undefined4 *)(unaff_r4 + 0xc),_DAT_0059df80);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    in_stack_00000004 = _DAT_0059df84;
    uStack00000000 = 0x73;
    FUN_0043d574(4,DAT_0059defc,DAT_0059def8,_DAT_0059df88);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,_DAT_0059e240);
  }
  return CONCAT44(in_stack_00000004,uStack00000000);
}

