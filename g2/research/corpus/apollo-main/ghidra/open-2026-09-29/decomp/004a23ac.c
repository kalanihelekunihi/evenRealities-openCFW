
void APP_MasterSysStartTryConnectRing(void)

{
  int iVar1;
  char local_20;
  char local_1f;
  char local_1e;
  char local_1d;
  char local_1c;
  char local_1b;
  undefined1 auStack_18 [14];
  undefined1 local_a;
  
  iVar1 = central_is_ring_owner_side_004a2914();
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004a28f0,DAT_004a28ec,DAT_004a2c94,0x4d8,DAT_004a2c90);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_004a2c98,DAT_004a2c98);
    }
  }
  else {
    iVar1 = FUN_00466010();
    FUN_00439be4(&local_20,iVar1 + 0xc,6);
    FUN_00439be4(auStack_18,DAT_004a290c,0xe);
    FUN_0043dacc(DAT_004a2e88,0x10,&local_20,6);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004a28f0,DAT_004a28ec,DAT_004a2c94,0x4e1,DAT_004a2e8c,local_1b,local_1c,
                   local_1d,local_1e,local_1f,local_20);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xd800000,DAT_004a2e90,DAT_004a2e90,local_1b,local_1c,local_1d,local_1e,
                          local_1f,local_20);
    }
    if (((((local_1b == -1) && (local_1c == -1)) && (local_1d == -1)) &&
        ((local_1e == -1 && (local_1f == -1)))) && (local_20 == -1)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004a28f0,DAT_004a28ec,DAT_004a2c94,0x4e3,DAT_004a2e94);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004a2e98,DAT_004a2e98);
      }
    }
    else if (*DAT_004a26c0 == '\x03') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004a28f0,DAT_004a28ec,DAT_004a2c94,0x4e7,DAT_004a2e9c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004a2ea0,DAT_004a2ea0);
      }
    }
    else {
      local_a = 0;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004a28f0,DAT_004a28ec,DAT_004a2c94,0x4eb,DAT_004a2fbc,auStack_18);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004a2fc0,DAT_004a2fc0,auStack_18);
      }
      APP_MasterSetTargetAddrName(&local_20,auStack_18,0xf);
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004a28f0,DAT_004a28ec,DAT_004a2c94,0x4ed,DAT_004a2fc4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004a2fc8,DAT_004a2fc8);
      }
      auth_mode_set(1);
      *DAT_004a2fb4 = 0;
      central_schedule_master_connect_004a2618(2000,0);
    }
  }
  return;
}

