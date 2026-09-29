
void INP_ThreadHandler(void)

{
  uint uVar1;
  int iVar2;
  undefined4 in_r3;
  undefined1 auStack_28 [2];
  char local_26;
  undefined4 local_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  local_18 = 0;
  uStack_14 = 0;
  uStack_10 = 0;
  uStack_c = in_r3;
  FUN_0043c0e4(auStack_28,0x10,0);
  thread_input_state_enter();
  INP_HardwareInit();
  INP_ResourceInit();
  FUN_004d3554(auStack_28);
  if (local_26 != '\0') {
    DRV_BuzzerPlay(8);
  }
  thread_input_state_exit();
  do {
    do {
      while ((uVar1 = osThreadFlagsWait(0xffffff,0,0xffffffff), uVar1 != 0 && (uVar1 < 0x80000000)))
      {
        input_flags_dispatch();
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_thread_input_005134c8,DAT_005134c4,DAT_00513504,0xb5,DAT_00513500);
      }
      iVar2 = FUN_0043d0ce();
    } while ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d));
    compress_log_output(0x4000000,DAT_00513508);
  } while( true );
}

