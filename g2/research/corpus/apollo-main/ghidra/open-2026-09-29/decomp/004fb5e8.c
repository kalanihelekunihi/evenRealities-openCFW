
undefined4 FUN_004fb5e8(void)

{
  int *piVar1;
  int iVar2;
  undefined4 in_r3;
  undefined1 local_14;
  undefined1 local_13;
  undefined1 local_12;
  undefined1 local_11;
  undefined1 local_10;
  undefined4 uStack_c;
  
  piVar1 = DAT_004fc1d4;
  uStack_c = in_r3;
  if (*DAT_004fc1c4 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004fb70c,DAT_004fb708,DAT_004fc1cc,0x233,DAT_004fc1c8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004fc1d0,DAT_004fc1d0);
    }
  }
  else {
    if (*(int *)(DAT_004fc1d8 + *DAT_004fc1d4 * 8 + 4) != 0) {
      FUN_0044d878(*(undefined4 *)(DAT_004fc1d8 + *DAT_004fc1d4 * 8 + 4));
    }
    FUN_004fb760(*piVar1);
    piVar1 = DAT_004fb744;
    if (((*DAT_004fb740 == 1) && (*DAT_004fb73c != 0)) && (*DAT_004fb744 != 0)) {
      if (*DAT_004fb738 == 0) {
        FUN_0044d878(*DAT_004fb744);
        FUN_004fc644(*piVar1);
      }
      else {
        local_14 = 0x47;
        local_13 = 0;
        local_12 = 0;
        local_11 = 0;
        local_10 = 0;
        ui_common_api_fn_00509ca2(*DAT_004fb73c,&local_14,5);
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004fb70c,DAT_004fb708,DAT_004fc1cc,0x248,DAT_004fc33c,local_14);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_004fc340,DAT_004fc340,local_14);
        }
      }
    }
  }
  return 0;
}

