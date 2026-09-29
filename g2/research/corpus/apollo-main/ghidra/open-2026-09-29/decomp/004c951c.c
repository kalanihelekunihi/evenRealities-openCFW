
undefined4 FUN_004c951c(void)

{
  undefined4 unaff_r7;
  
  fw_event_loop_initialize();
  FUN_004c953e();
  fw_event_loop_push_delayed(PTR_service_time_sync_callback_1_004c9c6c,0,10000);
  AT_CoreInit();
  FUN_0047e232();
  return unaff_r7;
}

