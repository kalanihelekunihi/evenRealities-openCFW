
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
DRV_Gx8002_I2SInit(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined *puVar3;
  int iVar4;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  uStack_18 = param_3;
  uStack_14 = param_4;
  if (*_DAT_0057a8bc == '\0') {
    *_DAT_0057a8bc = '\x01';
    func_0x004c3074(0,0);
    puVar1 = DAT_0057a880;
    func_0x0059005e(0,DAT_0057a880);
    func_0x00590648(*puVar1,0,0);
    uVar2 = DAT_0057a884;
    FUN_00590104(*puVar1,DAT_0057a884);
    FUN_00590b92(*puVar1);
    func_0x00590a24(*puVar1,uVar2,_DAT_0057a8cc);
    puVar3 = PTR_DAT_0057a8d0;
    __NVIC_SetPriority((int)*(short *)PTR_DAT_0057a8d0,4);
    __NVIC_EnableIRQ((int)*(short *)puVar3);
    FUN_00473934();
    FUN_005904ce(*puVar1,uVar2);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uStack_14 = PTR_s_gx8002b_i2s_init__0057a8d4;
      uStack_18 = 0x89;
      FUN_0043d574(4,DAT_0057a898,DAT_0057a894,PTR_s_DRV_Gx8002_I2SInit_0057a8c4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__drv_audio_codec_gx8002b_i2s_ini_0057a8d8);
    }
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uStack_14 = PTR_s_gx8002b_i2s_already_init__0057a8c0;
      uStack_18 = 0x79;
      FUN_0043d574(4,DAT_0057a898,DAT_0057a894,PTR_s_DRV_Gx8002_I2SInit_0057a8c4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__drv_audio_codec_gx8002b_i2s_alr_0057a8c8,
                          PTR_s__drv_audio_codec_gx8002b_i2s_alr_0057a8c8);
    }
  }
  return CONCAT44(uStack_14,uStack_18);
}

