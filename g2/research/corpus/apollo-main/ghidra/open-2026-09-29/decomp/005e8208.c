
undefined8 terminal_refresh_session_list_if_visible(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  
  if (*(char *)(DAT_005e8c04 + 0x275) == '\v') {
    if (*(char *)(DAT_005e8c04 + 0x27d) == '\0') {
      terminal_request_display(0x1c,0x40000000);
      uVar1 = 1;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        unaff_r5 = 0x37;
        FUN_0043d574(2,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_refresh_session_list_if_005e8c20,
                     0x37,DAT_005e8c1c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__terminal_pb_session_list_is_loa_005e8e38,
                            PTR_s__terminal_pb_session_list_is_loa_005e8e38);
      }
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 0;
  }
  return CONCAT44(unaff_r5,uVar1);
}

