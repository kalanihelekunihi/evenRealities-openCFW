
void tracepoint_handle_delete_file(undefined1 param_1,int param_2)

{
  undefined1 uVar1;
  int iVar2;
  bool bVar3;
  int local_68;
  undefined1 auStack_64 [80];
  
  bVar3 = true;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    iVar2 = DAT_005eefb4;
    if (param_2 != 0) {
      iVar2 = param_2;
    }
    uVar1 = tracepoint_role_char();
    local_68 = iVar2;
    FUN_0043d574(3,DAT_005ee79c,DAT_005ee798,DAT_005eefbc,0x162,DAT_005eefb8,param_1,uVar1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    iVar2 = DAT_005eefb4;
    if (param_2 != 0) {
      iVar2 = param_2;
    }
    uVar1 = tracepoint_role_char();
    compress_log_output(0xcc00000,DAT_005eefc0,DAT_005eefc0,param_1,uVar1,iVar2);
  }
  iVar2 = tracepoint_map_requested_file(param_2,auStack_64,0x50);
  if (iVar2 == 0) {
    local_68 = 0;
    iVar2 = tracepoint_resolve_file_name(auStack_64,&local_68);
    if (iVar2 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_005ee79c,DAT_005ee798,DAT_005eefbc,0x169,DAT_005eefc4,auStack_64,local_68
                    );
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_005eefc8,DAT_005eefc8,auStack_64,local_68);
      }
      FUN_0047e088();
      iVar2 = file_remove(auStack_64);
      bVar3 = iVar2 != 0;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005ee79c,DAT_005ee798,DAT_005eefbc,0x16c,DAT_005eefcc,auStack_64,bVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc800000,DAT_005eefd0,DAT_005eefd0,auStack_64,bVar3);
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      iVar2 = DAT_005eefb4;
      if (param_2 != 0) {
        iVar2 = param_2;
      }
      FUN_0043d574(2,DAT_005ee79c,DAT_005ee798,DAT_005eefbc,0x16f,DAT_005eefd4,iVar2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      if (param_2 == 0) {
        param_2 = DAT_005eefb4;
      }
      compress_log_output(0x8400000,PTR_s__tp_setting_invalid_tracepoint_d_005eefd8,
                          PTR_s__tp_setting_invalid_tracepoint_d_005eefd8,param_2);
    }
  }
  tracepoint_make_result_message(2,param_1,bVar3);
  tracepoint_reply_result(DAT_005eeb60);
  return;
}

