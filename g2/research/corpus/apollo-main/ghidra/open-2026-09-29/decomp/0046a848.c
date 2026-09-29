
void system_close_handle_click(void)

{
  int iVar1;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0046b058,DAT_0046b054,DAT_0046b050,0x1f8,DAT_0046b04c,*DAT_0046ae98,
                 *DAT_0046b00c);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_0046b05c,DAT_0046b05c,*DAT_0046ae98,*DAT_0046b00c);
  }
  if (*DAT_0046b00c == 2) {
    if (*DAT_0046ae98 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0046b058,DAT_0046b054,DAT_0046b050,0x1fe,DAT_0046b060);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_0046b064,DAT_0046b064);
      }
      iVar1 = FUN_0045a568();
      if (iVar1 == 1) {
        FUN_00464c36(0x22,0,0,0);
      }
    }
    else if (*DAT_0046ae98 == 1) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0046b058,DAT_0046b054,DAT_0046b050,0x203,DAT_0046b068);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_0046b06c,DAT_0046b06c);
      }
      iVar1 = FUN_0045a568();
      if (iVar1 == 1) {
        FUN_00464c36(0x22,0,0,0);
        FUN_0045accc(6,0xf,0,500);
      }
    }
  }
  else if (*DAT_0046b00c == 3) {
    if (*DAT_0046ae98 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0046b058,DAT_0046b054,DAT_0046b050,0x20c,DAT_0046b060);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0046b064,DAT_0046b064);
      }
      iVar1 = FUN_0045a568();
      if (iVar1 == 1) {
        FUN_00464c36(0x22,0,0,0);
      }
    }
    else if (*DAT_0046ae98 == 1) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0046b058,DAT_0046b054,DAT_0046b050,0x211,DAT_0046b070);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__system_close_User_selected__MIN_0046b074,
                            PTR_s__system_close_User_selected__MIN_0046b074);
      }
    }
    else if (*DAT_0046ae98 == 2) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0046b058,DAT_0046b054,DAT_0046b050,0x214,DAT_0046b068);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0046b06c,DAT_0046b06c);
      }
      iVar1 = FUN_0045a568();
      if (iVar1 == 1) {
        FUN_00464c36(0x22,0,0,0);
        FUN_0045accc(6,0xf,0,500);
      }
    }
  }
  return;
}

