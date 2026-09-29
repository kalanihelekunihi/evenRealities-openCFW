
undefined4 even_ai_timer_deinit_all(void)

{
  undefined4 unaff_r7;
  
  even_ai_common_timer_mgr_deinit();
  even_ai_heartbeat_timer_mgr_deinit();
  return unaff_r7;
}

