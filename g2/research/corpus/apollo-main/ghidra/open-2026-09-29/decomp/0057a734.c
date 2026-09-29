
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
DRV_Gx8002_I2SDeinit(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  if (*_DAT_0057a8bc == '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_c = PTR_s_gx8002b_i2s_already_deinit__0057a8dc;
      uStack_10 = 0x8f;
      FUN_0043d574(4,DAT_0057a898,DAT_0057a894,PTR_s_DRV_Gx8002_I2SDeinit_0057a8e0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__drv_audio_codec_gx8002b_i2s_alr_0057a8e4,
                          PTR_s__drv_audio_codec_gx8002b_i2s_alr_0057a8e4);
    }
  }
  else {
    *_DAT_0057a8bc = '\0';
    __NVIC_DisableIRQ((int)*(short *)PTR_DAT_0057a8d0);
    func_0x004c3138(0,0);
    puVar1 = DAT_0057a880;
    func_0x00590648(*DAT_0057a880,1,0);
    func_0x00590c62(*puVar1);
    func_0x005900ce(*puVar1);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_c = PTR_s_gx8002b_i2s_deinit__0057a8e8;
      uStack_10 = 0x99;
      FUN_0043d574(4,DAT_0057a898,DAT_0057a894,PTR_s_DRV_Gx8002_I2SDeinit_0057a8e0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__drv_audio_codec_gx8002b_i2s_dei_0057a8ec,
                          PTR_s__drv_audio_codec_gx8002b_i2s_dei_0057a8ec);
    }
  }
  return CONCAT44(uStack_c,uStack_10);
}

