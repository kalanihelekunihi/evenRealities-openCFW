
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0049c89e(undefined4 param_1,undefined *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  
  for (iVar4 = 0; iVar4 < *_DAT_0049cdc8; iVar4 = iVar4 + 1) {
    if (*(int *)(_DAT_0049cdb4 + iVar4 * 4) != 0) {
      uVar5 = *(undefined4 *)(_DAT_0049cdb4 + iVar4 * 4);
      uVar1 = FUN_0044104c(_DAT_0049cdb8);
      uVar2 = FUN_0049c070(uVar5,0);
      iVar3 = FUN_0044102e(uVar2,uVar1);
      if (iVar3 != 0) {
        uVar1 = FUN_0044104c(0xffffff);
        FUN_0044127e(uVar5,uVar1,0);
        FUN_0044129e(uVar5,0xff,0);
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          param_1 = 0x164;
          param_2 = PTR_s_Resumed_tile_indicator__d__0049cdcc;
          FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,PTR_s_resume_tile_indicators_0049cdd0
                       ,0x164,PTR_s_Resumed_tile_indicator__d__0049cdcc,iVar4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__dashboard_Resumed_tile_indicato_0049cdd4,
                              PTR_s__dashboard_Resumed_tile_indicato_0049cdd4,iVar4);
        }
      }
    }
  }
  return CONCAT44(param_2,param_1);
}

