
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_005e7f26(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  if (*_DAT_005e8124 != '\0') {
    *_DAT_005e8124 = '\0';
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_voice_timeout_stop_005e813c;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x39;
      FUN_0043d574(4,PTR_s_terminal_timer_005e8134,PTR_s_D__01_workspace_s200_ap510b_iar__005e8130,
                   PTR_s_terminal_timer_voice_timeout_sto_005e8140);
      unaff_r6 = puVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__terminal_timer_voice_timeout_st_005e8144,
                          PTR_s__terminal_timer_voice_timeout_st_005e8144);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

