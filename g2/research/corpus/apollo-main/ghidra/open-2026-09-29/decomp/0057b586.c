
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
DRV_PdmProductionDeinit(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  if (*_DAT_0057b6b8 == '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_c = PTR_s_pdm_already_deinit__0057b6e8;
      uStack_10 = 0x79;
      FUN_0043d574(4,PTR_s_drv_audio_pdm_production_0057b6c8,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0057b6c4,
                   PTR_s_DRV_PdmProductionDeinit_0057b6ec);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__drv_audio_pdm_production_pdm_al_0057b6f0,
                          PTR_s__drv_audio_pdm_production_pdm_al_0057b6f0);
    }
  }
  else {
    *_DAT_0057b6b8 = '\0';
    puVar1 = DAT_0057b6d0;
    FUN_005925b4(*DAT_0057b6d0,0x18);
    FUN_00592584(*puVar1,0x18);
    __NVIC_DisableIRQ((int)*_DAT_0057b6d8);
    func_0x004c3204(0);
    func_0x005922d6(*puVar1);
    func_0x00592046(*puVar1,1,0);
    func_0x00592014(*puVar1);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_c = PTR_s_PDM_deinit_0057b6f4;
      uStack_10 = 0x89;
      FUN_0043d574(3,PTR_s_drv_audio_pdm_production_0057b6c8,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0057b6c4,
                   PTR_s_DRV_PdmProductionDeinit_0057b6ec);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__drv_audio_pdm_production_PDM_de_0057b6f8,
                          PTR_s__drv_audio_pdm_production_PDM_de_0057b6f8);
    }
  }
  return CONCAT44(uStack_c,uStack_10);
}

