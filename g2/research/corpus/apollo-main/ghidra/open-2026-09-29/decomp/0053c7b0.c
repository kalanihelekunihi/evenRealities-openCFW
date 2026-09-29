
undefined8 AUD_PdmCtr(int param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = *(uint *)(param_1 + 8);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = uVar2 & 0xff;
    param_1 = 0x15d;
    param_2 = PTR_s_pdm_ctr___d_0053cee4;
    FUN_0043d574(3,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_PdmCtr_0053cee8,0x15d,
                 PTR_s_pdm_ctr___d_0053cee4,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__thread_audio_pdm_ctr___d_0053ceec,
                        PTR_s__thread_audio_pdm_ctr___d_0053ceec,uVar2 & 0xff,param_1,param_2,
                        param_3);
  }
  iVar1 = productModeGet();
  if ((iVar1 == 1) && (*DAT_0053cee0 == '\0')) {
    if ((uVar2 & 0xff) == 0) {
      DRV_PdmProductionDeinit();
    }
    else {
      DRV_PdmProductionInit();
    }
  }
  else if ((uVar2 & 0xff) == 0) {
    DRV_PdmDeinit();
  }
  else {
    DRV_PdmInit();
  }
  return CONCAT44(param_2,param_1);
}

