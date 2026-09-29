
longlong INP_BoxDetectInCase(void)

{
  undefined *puVar1;
  int iVar2;
  undefined *unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_Box_detect_in_case__reset_touch_a_00513520;
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_thread_input_005134c8,DAT_005134c4,PTR_s_INP_BoxDetectInCase_00513524);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_00513122;
  }
  compress_log_output(0xc000000,PTR_s__thread_input_Box_detect_in_case_00513528,
                      PTR_s__thread_input_Box_detect_in_case_00513528);
LAB_00513122:
  FUN_0055b64a();
  FUN_0055b6dc(&stack0xfffffff0);
  FUN_0055b730();
  return ZEXT48(unaff_r6) << 0x20;
}

