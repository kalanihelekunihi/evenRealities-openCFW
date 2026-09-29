
undefined4
am_devices_jbd4010_set_display_offset
          (byte param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  byte local_18;
  byte local_17;
  undefined4 local_14;
  undefined4 uStack_10;
  
  local_14 = 0;
  uStack_10 = param_4;
  if ((*DAT_0059364c != '\0') && (iVar1 = FUN_0045a568(), iVar1 == 2)) {
    param_1 = param_1 + 5;
  }
  if (param_1 < 2) {
    param_1 = 2;
  }
  if (0x16 < param_1) {
    param_1 = 0x16;
  }
  if (param_2 < 2) {
    param_2 = 2;
  }
  if (0x12 < param_2) {
    param_2 = 0x12;
  }
  iVar1 = jbd4010_write_command(0xa9,&local_14,0);
  if (iVar1 == 0) {
    local_18 = param_1;
    local_17 = param_2;
    iVar1 = jbd4010_write_command(0xc0,&local_18,2);
    if (iVar1 == 0) {
      iVar1 = jbd4010_write_command(0xa3,&local_14,0);
      if (iVar1 == 0) {
        jbd4010_write_command(0x97,&local_14,0);
        FUN_004910f4(1);
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(3,DAT_00593320,DAT_0059331c,DAT_00593654,0x18c,DAT_00593748,param_1,param_2);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0xc800000,DAT_005938cc,DAT_005938cc,param_1,param_2);
        }
        uVar2 = 0;
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00593320,DAT_0059331c,DAT_00593654,0x185,DAT_00593740);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00593744,DAT_00593744);
        }
        uVar2 = 0xffffffff;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00593320,DAT_0059331c,DAT_00593654,0x17e,DAT_0059365c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0059373c,DAT_0059373c);
      }
      uVar2 = 0xffffffff;
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00593320,DAT_0059331c,DAT_00593654,0x175,DAT_00593650);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00593658);
    }
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

