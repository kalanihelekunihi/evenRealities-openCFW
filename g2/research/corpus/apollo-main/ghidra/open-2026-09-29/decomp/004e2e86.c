
undefined8 even_ai_common_timer_mgr_stop(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar2 = DAT_004e3130;
  *(undefined1 *)(DAT_004e3130 + 9) = 0;
  *(undefined1 *)(iVar2 + 8) = 0;
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_even_ai_common_timer_mgr_stop_004e3148;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x39;
    FUN_0043d574(4,DAT_004e3138,DAT_004e3134,PTR_s_even_ai_common_timer_mgr_stop_004e314c);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__even_ai_timer_even_ai_common_ti_004e3150,
                        PTR_s__even_ai_timer_even_ai_common_ti_004e3150);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

