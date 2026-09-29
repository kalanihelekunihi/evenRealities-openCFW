
longlong terminal_action_heart_beat(void)

{
  int iVar1;
  uint unaff_r5;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0x289;
    FUN_0043d574(3,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                 PTR_s_terminal_action_heart_beat_005ea19c,0x289,
                 PTR_s_recv_terminal_heart_beat_005ea198);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__terminal_pb_recv_terminal_heart_005ea1a0,
                        PTR_s__terminal_pb_recv_terminal_heart_005ea1a0);
  }
  return (ulonglong)unaff_r5 << 0x20;
}

