
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
DRV_PdmProductionInit(undefined4 param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  short *psVar2;
  int iVar3;
  
  if (*_DAT_0057b6b8 == '\0') {
    *_DAT_0057b6b8 = '\x01';
    func_0x004c31d8(0);
    FUN_0053a5be(0x8f,1);
    puVar1 = DAT_0057b6d0;
    func_0x00591fac(0,DAT_0057b6d0);
    func_0x00592046(*puVar1,0,0);
    func_0x005920cc(*puVar1,_DAT_0057b6d4);
    func_0x00592462(*puVar1,0x10);
    FUN_00592556(*puVar1,0x18);
    psVar2 = _DAT_0057b6d8;
    __NVIC_SetPriority((int)*_DAT_0057b6d8,4);
    __NVIC_EnableIRQ((int)*psVar2);
    func_0x00592230(*puVar1);
    func_0x0059235e(*puVar1,_DAT_0057b6dc);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x73;
      param_3 = PTR_s_PDM_init_0057b6e0;
      FUN_0043d574(3,PTR_s_drv_audio_pdm_production_0057b6c8,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0057b6c4,
                   PTR_s_DRV_PdmProductionInit_0057b6c0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__drv_audio_pdm_production_PDM_in_0057b6e4,
                          PTR_s__drv_audio_pdm_production_PDM_in_0057b6e4);
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x5c;
      param_3 = PTR_s_pdm_already_init__0057b6bc;
      FUN_0043d574(4,PTR_s_drv_audio_pdm_production_0057b6c8,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0057b6c4,
                   PTR_s_DRV_PdmProductionInit_0057b6c0,0x5c,PTR_s_pdm_already_init__0057b6bc,
                   param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__drv_audio_pdm_production_pdm_al_0057b6cc,
                          PTR_s__drv_audio_pdm_production_pdm_al_0057b6cc);
    }
  }
  return CONCAT44(param_3,param_2);
}

