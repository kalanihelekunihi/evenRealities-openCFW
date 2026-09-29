
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
AUD_ResourceInit(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = DAT_0053cd94;
  uVar2 = osMessageQueueNew(0x32,0xc,0);
  *(undefined4 *)(iVar3 + 0xc) = uVar2;
  if (*(int *)(iVar3 + 0xc) == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0xc2;
      param_2 = PTR_s_osMessageQueueNew_fail_0053ce80;
      FUN_0043d574(1,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_ResourceInit_0053ce84,0xc2,
                   PTR_s_osMessageQueueNew_fail_0053ce80,param_3,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__thread_audio_osMessageQueueNew_f_0053ce88);
    }
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      param_1 = 0xc4;
      param_2 = PTR_s_osMessageQueueNew_0x_x__success_0053ce8c;
      FUN_0043d574(4,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_ResourceInit_0053ce84,0xc4,
                   PTR_s_osMessageQueueNew_0x_x__success_0053ce8c,*(undefined4 *)(iVar3 + 0xc),
                   param_4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__thread_audio_osMessageQueueNew__0053ce90,
                          PTR_s__thread_audio_osMessageQueueNew__0053ce90,
                          *(undefined4 *)(iVar3 + 0xc));
    }
  }
  piVar1 = _DAT_0053ce74;
  iVar3 = osTimerNew(PTR_FUN_0053c2a4_1_0053ce98,0,0,PTR_DAT_0053ce94);
  *piVar1 = iVar3;
  if (*piVar1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0xc9;
      param_2 = PTR_s_codec_audio_check_timer_create_f_0053ce9c;
      FUN_0043d574(1,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_ResourceInit_0053ce84);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__thread_audio_codec_audio_check_t_0053cea0,
                          PTR_s__thread_audio_codec_audio_check_t_0053cea0);
    }
  }
  return CONCAT44(param_2,param_1);
}

