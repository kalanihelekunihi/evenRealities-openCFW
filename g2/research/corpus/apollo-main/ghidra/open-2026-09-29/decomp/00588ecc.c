
undefined8 FUN_00588ecc(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_Auto_scroll_timer_stop_00589398;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 100;
    FUN_0043d574(3,DAT_00589364,DAT_00589360,PTR_s_teleprompt_timer_auto_scroll_sto_0058939c);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__teleprompt_timer_Auto_scroll_ti_005893a0,
                        PTR_s__teleprompt_timer_Auto_scroll_ti_005893a0);
  }
  *DAT_00589384 = 0;
  return CONCAT44(unaff_r6,unaff_r5);
}

