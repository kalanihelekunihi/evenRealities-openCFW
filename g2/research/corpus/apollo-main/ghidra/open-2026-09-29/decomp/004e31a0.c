
undefined4 even_ai_timer_start_all(void)

{
  undefined4 unaff_r7;
  
  even_ai_common_timer_mgr_start();
  even_ai_heartbeat_timer_mgr_start(10000);
  return unaff_r7;
}

