
undefined4 FUN_005455e4(void)

{
  int iVar1;
  undefined4 uVar2;
  
  *DAT_00545cb4 = 1;
  *DAT_00545cb8 = 0;
  iVar1 = HUB_Open(2);
  if (iVar1 == 0) {
    iVar1 = HUB_ParameterConfig(2,&stack0xfffffff0);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00545cc8,DAT_00545cc4,DAT_00545cc0,0x10b,DAT_00545cbc);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__navigation_ui_StartIMUComassFun_00545ccc,
                            PTR_s__navigation_ui_StartIMUComassFun_00545ccc);
      }
      uVar2 = 0;
    }
    else {
      uVar2 = 0xffffffff;
    }
  }
  else {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

