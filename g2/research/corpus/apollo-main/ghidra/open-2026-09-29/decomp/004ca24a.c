
undefined8 uled_set_display_offset(undefined1 param_1,undefined1 param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if (*DAT_004ca664 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0xe5;
      FUN_0043d574(1,DAT_004ca674,DAT_004ca670,DAT_004ca6dc,0xe5,DAT_004ca668);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ca678,DAT_004ca678);
    }
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = (**(code **)(*DAT_004ca664 + 0x24))(param_1,param_2);
  }
  return CONCAT44(unaff_r5,uVar2);
}

