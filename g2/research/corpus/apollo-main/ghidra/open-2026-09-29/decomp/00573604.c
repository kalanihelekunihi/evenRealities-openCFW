
undefined4 pt_cmd_3A_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  float local_38 [9];
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00573f80,DAT_00573f7c,DAT_00573f78,0x938,DAT_00573f74);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00573654;
  }
  compress_log_output(0xc000000,DAT_00573f84,DAT_00573f84);
LAB_00573654:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     (param_2 < 0x28)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00573f80,DAT_00573f7c,DAT_00573f78,0x93b,DAT_00573c20,DAT_00573f78);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00573c30,DAT_00573c30,DAT_00573f78);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x2d;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    iVar1 = productModeGet();
    if (iVar1 == 1) {
      FUN_0048949c(local_38,0x24);
      for (iVar1 = 0; iVar1 < 9; iVar1 = iVar1 + 1) {
        local_38[iVar1] = *(float *)(param_1 + 4 + iVar1 * 4);
      }
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00573f80,DAT_00573f7c,DAT_00573f78,0x950,DAT_005741d4,(double)local_38[0]
                     ,(double)local_38[1],(double)local_38[2],(double)local_38[3],
                     (double)local_38[4],(double)local_38[5],(double)local_38[6],(double)local_38[7]
                     ,(double)local_38[8]);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xe400000,DAT_005741d8,DAT_005741d8);
      }
      nvdbSensorCaldataAgUpdate(0,0,local_38);
      param_3[4] = 0;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00573f80,DAT_00573f7c,DAT_00573f78,0x956,DAT_00573f68);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0057456c,DAT_0057456c);
      }
      param_3[4] = 5;
    }
    *param_4 = 5;
    uVar2 = 0;
  }
  return uVar2;
}

