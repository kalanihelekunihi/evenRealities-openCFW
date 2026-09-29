
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
AUD_ThreadInit(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_0053cd94;
  uVar1 = osThreadNew(0x53c52d,0,_DAT_0053cd98);
  *(undefined4 *)(iVar2 + 8) = uVar1;
  if (*(int *)(iVar2 + 8) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0xb8;
      param_2 = PTR_s_osThreadNew_fail_0053cd9c;
      FUN_0043d574(1,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_ThreadInit_0053cda0,0xb8,
                   PTR_s_osThreadNew_fail_0053cd9c,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__thread_audio_osThreadNew_fail_0053cda4);
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0xba;
      param_2 = PTR_s_osThreadNew_0x_x__success_0053cda8;
      FUN_0043d574(4,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_ThreadInit_0053cda0,0xba,
                   PTR_s_osThreadNew_0x_x__success_0053cda8,*(undefined4 *)(iVar2 + 8),param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__thread_audio_osThreadNew_0x_x__s_0053ce7c,
                          PTR_s__thread_audio_osThreadNew_0x_x__s_0053ce7c,
                          *(undefined4 *)(iVar2 + 8));
    }
  }
  return CONCAT44(param_2,param_1);
}

