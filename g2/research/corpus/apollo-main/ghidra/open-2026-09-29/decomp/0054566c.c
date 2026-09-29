
undefined8 FUN_0054566c(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  *DAT_00545cb4 = 0;
  *DAT_00545cb8 = 0;
  iVar1 = HUB_Close(2);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x114;
      FUN_0043d574(1,DAT_00545cc8,DAT_00545cc4,PTR_s_StopIMUCompassFunc_00545cd4,0x114,
                   PTR_s_StopIMUComassFunc__HUB_Close_fai_00545cd0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__navigation_ui_StopIMUComassFunc_00545cd8,
                          PTR_s__navigation_ui_StopIMUComassFunc_00545cd8);
    }
    uVar2 = 0xffffffff;
  }
  return CONCAT44(unaff_r5,uVar2);
}

