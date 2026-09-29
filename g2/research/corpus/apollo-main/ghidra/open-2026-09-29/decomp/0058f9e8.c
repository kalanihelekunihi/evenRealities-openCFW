
undefined4 _nvdbUpdataBuzzer(void)

{
  int iVar1;
  byte abStack_10 [10];
  short sStack_6;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(2,PTR_s_nv_buzzer_0058faa0,PTR_s_D__01_workspace_s200_ap510b_iar__0058fa9c,
                 PTR_s__nvdbUpdataBuzzer_0058fa98,0x2e,
                 PTR_s___This_is_only_for_program_debug_0058fa94);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x8000000,PTR_s__nv_buzzer___This_is_only_for_pr_0058faa4,
                        PTR_s__nv_buzzer___This_is_only_for_pr_0058faa4);
  }
  iVar1 = SVC_NvdbRead(DAT_0058faa8,abStack_10,0xc);
  if (iVar1 < 1) {
    nvdbBuzzerUpdate(*(undefined4 *)(DAT_0058fa90 + 4),*(undefined1 *)(DAT_0058fa90 + 8));
  }
  else if ((sStack_6 != *(short *)(DAT_0058fa90 + 10)) && (abStack_10[0] < 2)) {
    nvdbBuzzerUpdate(*(undefined4 *)(DAT_0058fa90 + 4),*(undefined1 *)(DAT_0058fa90 + 8));
  }
  return 0;
}

