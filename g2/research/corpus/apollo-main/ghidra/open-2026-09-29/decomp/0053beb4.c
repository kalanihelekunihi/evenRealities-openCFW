
void bq27427_settings(void)

{
  int iVar1;
  int local_14;
  int local_10;
  int local_c;
  
  local_14 = *DAT_0053c250;
  local_10 = DAT_0053c250[1];
  local_c = DAT_0053c250[2];
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0053c238,DAT_0053c234,DAT_0053c258,0x28d,DAT_0053c254,local_14,local_10,
                 local_c);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10c00000,DAT_0053c25c,DAT_0053c25c,local_14,local_10,local_c);
  }
  if (local_14 < 0x92fc) {
    if (local_10 < 0x1f41) {
      if (local_c - 0x9c4U < 0x4b1) {
        bq27427_configure_from_params(&local_14);
        bq27427_change_chemistry_profile();
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0053c238,DAT_0053c234,DAT_0053c258,0x299,DAT_0053c270,local_c);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_0053c274,DAT_0053c274,local_c);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0053c238,DAT_0053c234,DAT_0053c258,0x294,DAT_0053c268,local_10);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0053c26c,DAT_0053c26c,local_10);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0053c238,DAT_0053c234,DAT_0053c258,0x28f,DAT_0053c260,local_14);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0053c264,DAT_0053c264,local_14);
    }
  }
  return;
}

