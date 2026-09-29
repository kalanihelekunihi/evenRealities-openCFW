
undefined4 jdb4010_status_check(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  char local_14 [8];
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  FUN_0043c0e4(local_14,8,0);
  iVar1 = jbd4010_read_response(5,local_14,1);
  if (iVar1 == 0) {
    if (local_14[0] == -0x70) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00593900,DAT_005938fc,DAT_0059393c,0x2dd,DAT_00593944,local_14[0]);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_00593948,DAT_00593948,local_14[0]);
      }
      uVar3 = 0xffffffff;
    }
    else {
      iVar1 = jbd4010_read_response(0x35,local_14,1);
      if (iVar1 == 0) {
        if (local_14[0] == '\0') {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(2,DAT_00593900,DAT_005938fc,DAT_0059393c,0x2e6,DAT_00593954,local_14[0]);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x8400000,PTR_s__driver_jbd4010_read_status_reg_f_00593958,
                                PTR_s__driver_jbd4010_read_status_reg_f_00593958,local_14[0]);
          }
          uVar3 = 0xffffffff;
        }
        else {
          uVar3 = 0;
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00593900,DAT_005938fc,DAT_0059393c,0x2e3,DAT_0059394c,iVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_00593950,DAT_00593950,iVar1);
        }
        uVar3 = 0xffffffff;
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00593900,DAT_005938fc,DAT_0059393c,0x2da,DAT_00593938,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00593940,DAT_00593940,iVar1);
    }
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

