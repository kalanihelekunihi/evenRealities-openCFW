
undefined8 FUN_0058a5a4(int param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined4 uStack_18;
  undefined *puStack_14;
  
  piVar1 = DAT_0058a86c;
  piVar2 = *(int **)(param_1 + 0x1c);
  uStack_18 = param_3;
  puStack_14 = param_4;
  if (piVar2 == (int *)0x0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      puStack_14 = PTR_s_phase2_ready_cb__invalid_context_0058a88c;
      uStack_18 = 0x7d;
      FUN_0043d574(1,PTR_s_bounce_anim_0058a864,PTR_s_D__01_workspace_s200_ap510b_iar__0058a860,
                   PTR_s_bounce_anim_phase2_ready_cb_0058a890);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__bounce_anim_phase2_ready_cb__in_0058a894,
                          PTR_s__bounce_anim_phase2_ready_cb__in_0058a894);
    }
  }
  else if ((*DAT_0058a86c == *piVar2) && (piVar2 == DAT_0058a86c)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      puStack_14 = PTR_s_Bounce_animation_completed_0058a8a0;
      uStack_18 = 0x87;
      FUN_0043d574(3,PTR_s_bounce_anim_0058a864,PTR_s_D__01_workspace_s200_ap510b_iar__0058a860,
                   PTR_s_bounce_anim_phase2_ready_cb_0058a890);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__bounce_anim_Bounce_animation_co_0058a8a4,
                          PTR_s__bounce_anim_Bounce_animation_co_0058a8a4);
    }
    if (piVar2[3] != 0) {
      (*(code *)piVar2[3])(param_1);
    }
    *piVar1 = 0;
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      puStack_14 = PTR_s_phase2_ready_cb__animation_was_s_0058a898;
      uStack_18 = 0x83;
      FUN_0043d574(4,PTR_s_bounce_anim_0058a864,PTR_s_D__01_workspace_s200_ap510b_iar__0058a860,
                   PTR_s_bounce_anim_phase2_ready_cb_0058a890);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__bounce_anim_phase2_ready_cb__an_0058a89c);
    }
  }
  return CONCAT44(puStack_14,uStack_18);
}

