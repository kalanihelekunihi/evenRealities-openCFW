
void FUN_004dfcc0(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 local_1c;
  undefined2 local_1b;
  undefined2 local_19;
  
  iVar3 = *(int *)(param_1 + 0x1c);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_common_text_container_004dfff4,
                 PTR_s_D__01_workspace_s200_ap510b_iar__004dfff0,
                 PTR_s_common_text_rubber_band_anim_com_004e02fc,0x216,
                 PTR_s_common_text_rubber_band_anim_com_004e02f8);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__common_text_container_common_te_004e0300,
                        PTR_s__common_text_container_common_te_004e0300);
  }
  if ((*(int *)(iVar3 + 4) != 0) && (iVar1 = FUN_0043fce0(*(undefined4 *)(iVar3 + 4)), iVar1 != 0))
  {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_common_text_container_004dfff4,
                   PTR_s_D__01_workspace_s200_ap510b_iar__004dfff0,
                   PTR_s_common_text_rubber_band_anim_com_004e02fc,0x21c,
                   PTR_s_Resetting_content_container_Y_fr_004e0304,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__common_text_container_Resetting_004e0308,
                          PTR_s__common_text_container_Resetting_004e0308,iVar1);
    }
    FUN_0043f142(*(undefined4 *)(iVar3 + 4),0);
  }
  *(undefined1 *)(iVar3 + 0x13) = 0;
  *(undefined4 *)(iVar3 + 0x14) = 0;
  iVar1 = ui_common_api_fn_00509dfa(*(undefined4 *)(iVar3 + 0x18));
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_common_text_container_004dfff4,
                   PTR_s_D__01_workspace_s200_ap510b_iar__004dfff0,
                   PTR_s_common_text_rubber_band_anim_com_004e02fc,0x227,
                   PTR_s_common_text_rubber_band_anim_com_004e030c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__common_text_container_common_te_004e0310,
                          PTR_s__common_text_container_common_te_004e0310);
    }
    iVar1 = ui_common_api_fn_00509e14(*(undefined4 *)(iVar3 + 0x18),&local_1c,5);
    if (iVar1 == 5) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_common_text_container_004dfff4,
                     PTR_s_D__01_workspace_s200_ap510b_iar__004dfff0,
                     PTR_s_common_text_rubber_band_anim_com_004e02fc,0x22d,
                     PTR_s_common_text_rubber_band_anim_com_004e0314,local_1c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__common_text_container_common_te_004e0318,
                            PTR_s__common_text_container_common_te_004e0318,local_1c);
      }
      FUN_004e033c(iVar3,local_1c,local_1b,local_19);
    }
  }
  return;
}

