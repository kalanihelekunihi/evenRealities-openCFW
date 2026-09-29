
undefined4 even_ai_timer_process_all(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = even_ai_common_timer_mgr_check_timeout();
  if (iVar1 != 0) {
    even_ai_common_timer_mgr_process_timeout();
  }
  iVar1 = even_ai_heartbeat_timer_mgr_check_timeout();
  if (iVar1 != 0) {
    even_ai_heartbeat_timer_mgr_process_timeout();
  }
  return unaff_r7;
}

