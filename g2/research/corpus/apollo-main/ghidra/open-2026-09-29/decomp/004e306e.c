
undefined8 even_ai_heartbeat_timer_mgr_stop(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = DAT_004e316c;
  *(undefined1 *)(DAT_004e316c + 9) = 0;
  *(undefined1 *)(iVar2 + 8) = 0;
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_004e317c;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0xc5;
    FUN_0043d574(4,DAT_004e3138,DAT_004e3134,DAT_004e3180);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__even_ai_timer_even_ai_heartbeat_004e3184,
                        PTR_s__even_ai_timer_even_ai_heartbeat_004e3184);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

