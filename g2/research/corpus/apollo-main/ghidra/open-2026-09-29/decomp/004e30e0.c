
undefined8 even_ai_heartbeat_timer_mgr_process_timeout(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  if (*(char *)(DAT_004e316c + 8) != '\x02') goto LAB_004e312e;
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_even_ai_heartbeat_timer__process_004e3188;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0xe1;
    FUN_0043d574(3,DAT_004e3138,DAT_004e3134,PTR_s_even_ai_heartbeat_timer_mgr_proc_004e318c);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_004e3116:
    compress_log_output(0xc000000,PTR_s__even_ai_timer_even_ai_heartbeat_004e3190,
                        PTR_s__even_ai_timer_even_ai_heartbeat_004e3190);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_004e3116;
  }
  even_ai_heartbeat_timer_mgr_stop();
  service_even_ai_fn_0049832e(3,0);
LAB_004e312e:
  return CONCAT44(unaff_r6,unaff_r5);
}

