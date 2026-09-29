
undefined4 pt_cmd_2D_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  char *pcVar3;
  undefined1 local_18;
  undefined1 local_17 [3];
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00570760,DAT_0057075c,DAT_00570d1c,0x44a,DAT_00570d18);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00570260;
  }
  compress_log_output(0xc000000,DAT_00570d20,DAT_00570d20);
LAB_00570260:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     (param_2 < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00570760,DAT_0057075c,DAT_00570d1c,0x44d,DAT_0057076c,DAT_00570d1c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00570770,DAT_00570770,DAT_00570d1c);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x38;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    iVar1 = productModeGet();
    if (iVar1 == 1) {
      local_17[0] = *(undefined1 *)(param_1 + 6);
      local_18 = *(undefined1 *)(param_1 + 8);
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00570760,DAT_0057075c,DAT_00570d1c,0x45c,DAT_00570d24,local_17[0],
                     local_18);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc800000,DAT_00570d28,DAT_00570d28,local_17[0],local_18);
      }
      iVar1 = DAT_00570d2c;
      *(undefined1 *)(DAT_00570d2c + 0x2c) = local_17[0];
      *(undefined1 *)(iVar1 + 0x2d) = local_18;
      param_3[4] = 0;
      if (*(char *)(param_1 + 4) != '\0') {
        SVC_NvdbWriteSysData(3,local_17);
        SVC_NvdbWriteSysData(4,&local_18);
      }
      pcVar3 = (char *)FUN_0044347a();
      if ((pcVar3 == (char *)0x0) || (*pcVar3 != '\x01')) {
        FUN_004441ec(0x10b,0,0);
        uled_mspi_setBrightness(100,0x1bbc,0x3f);
        FUN_0046c984(0x60);
        FUN_0046c9dc(0,0);
        FUN_0046c9aa(0x20);
      }
      uled_set_display_offset(local_17[0],local_18);
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00570760,DAT_0057075c,DAT_00570d1c,0x47b,DAT_00570d30);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00571024,DAT_00571024);
      }
      param_3[4] = 5;
    }
    *param_4 = 5;
    uVar2 = 0;
  }
  return uVar2;
}

