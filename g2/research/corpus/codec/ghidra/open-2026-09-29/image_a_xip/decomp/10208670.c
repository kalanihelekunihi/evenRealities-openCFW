
undefined4 gx8002_tws_init(int param_1)

{
  uint uVar1;
  int iVar2;
  
  LvpQueueInit(DAT_102086c8 + -0x14,DAT_102086c8,0x38,8);
  LvpInitMaxKws();
  uVar1 = func_0x10024940();
  gx8002_kws_initialize(DAT_102086cc,uVar1);
  if ((param_1 == 0xffff) && (1 < uVar1)) {
    gx8002_audio_input_standby_startup();
  }
  else {
    iVar2 = gx8002_audio_input_init(DAT_102086d0);
    if (iVar2 != 0) {
      gx8002_printf(PTR_s__LVP_TWS_LvpAudioInInit_Failed_102086d4);
      return 0xffffffff;
    }
  }
  iVar2 = DAT_102086d8;
  *(undefined4 *)(DAT_102086d8 + 0x4c) = 2;
  *(undefined4 *)(iVar2 + 0x50) = 0x32;
  return 0;
}

