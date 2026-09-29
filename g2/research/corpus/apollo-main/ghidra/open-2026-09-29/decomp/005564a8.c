
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005564a8(undefined4 param_1,uint param_2)

{
  uint *puVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  
  puVar1 = _DAT_00556eb4;
  iVar3 = _DAT_00556cbc;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_teleprompt_ui_00556ec4,PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                 PTR_s_teleprompt_ui_action_ai_sync_00556ebc,0x67d,PTR_s_Main_page_AI_sync_00556eb8)
    ;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__teleprompt_ui_Main_page_AI_sync_00556ec8);
  }
  iVar2 = FUN_0044dce2(*(undefined4 *)(iVar3 + 0x18),0);
  if (iVar2 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_teleprompt_ui_00556ec4,PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                   PTR_s_teleprompt_ui_action_ai_sync_00556ebc,0x681,PTR_s_label_is_NULL_00556ecc);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__teleprompt_ui_label_is_NULL_00556ed0,
                          PTR_s__teleprompt_ui_label_is_NULL_00556ed0);
    }
    uVar4 = 0xffffffff;
  }
  else {
    for (uVar6 = 0; uVar6 < 4; uVar6 = uVar6 + 1) {
      iVar2 = FUN_0044dce2(*(undefined4 *)(iVar3 + 0x18),uVar6);
      if (iVar2 != 0) {
        uVar5 = uVar6 + *(int *)(iVar3 + 0x2c);
        if (uVar5 < *puVar1) {
          FUN_00499716(iVar2,0);
          FUN_004997f8(iVar2);
          uVar4 = FUN_0044a43c();
          FUN_00499752(iVar2,uVar4);
        }
        else if (uVar5 == *puVar1) {
          FUN_00499716(iVar2,0);
          FUN_00499752(iVar2,puVar1[2]);
        }
        else {
          FUN_00499716(iVar2,0xffff);
          FUN_00499752(iVar2,0xffff);
        }
      }
    }
    uVar6 = param_2 / 10;
    param_2 = param_2 % 10;
    if ((uVar6 != *puVar1) || (param_2 != puVar1[1])) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_teleprompt_ui_00556ec4,PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                     PTR_s_teleprompt_ui_action_ai_sync_00556ebc,0x69e,_DAT_00557100,uVar6,param_2,
                     *puVar1,puVar1[1]);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x9000000,PTR_s__teleprompt_ui_ai_sync_payload_m_00557260,
                            PTR_s__teleprompt_ui_ai_sync_payload_m_00557260,uVar6,param_2,*puVar1,
                            puVar1[1]);
      }
    }
    uVar4 = FUN_00554a84(*(undefined4 *)(iVar3 + 0x18),uVar6,param_2,1);
    FUN_0044ea04(*(undefined4 *)(iVar3 + 0x18),uVar4,1);
    uVar4 = 0;
  }
  return uVar4;
}

