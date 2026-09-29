
void FUN_0058a408(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int aiStack_74 [4];
  undefined4 uStack_64;
  int *piStack_58;
  undefined *puStack_54;
  undefined4 uStack_44;
  undefined4 uStack_14;
  
  piVar1 = *(int **)(param_1 + 0x1c);
  uStack_14 = param_4;
  if ((piVar1 == (int *)0x0) || (*piVar1 == 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_bounce_anim_0058a864,PTR_s_D__01_workspace_s200_ap510b_iar__0058a860,
                   PTR_s_bounce_anim_phase1_ready_cb_0058a85c,0x44,
                   PTR_s_phase1_ready_cb__invalid_context_0058a858);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__bounce_anim_phase1_ready_cb__in_0058a868,
                          PTR_s__bounce_anim_phase1_ready_cb__in_0058a868);
    }
  }
  else if ((*DAT_0058a86c == *piVar1) && (piVar1 == DAT_0058a86c)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_bounce_anim_0058a864,PTR_s_D__01_workspace_s200_ap510b_iar__0058a860,
                   PTR_s_bounce_anim_phase1_ready_cb_0058a85c,0x4e,
                   PTR_s_Phase_1_completed__starting_phas_0058a878);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__bounce_anim_Phase_1_completed__s_0058a87c,
                          PTR_s__bounce_anim_Phase_1_completed__s_0058a87c);
    }
    if ((char)piVar1[2] == '\0') {
      iVar2 = piVar1[1] + -0x1e;
    }
    else {
      iVar2 = piVar1[1] + 0x1e;
    }
    FUN_004503d6(aiStack_74);
    aiStack_74[0] = *piVar1;
    aiStack_74[1] = 0x58a599;
    FUN_004506ce(aiStack_74,iVar2,piVar1[1]);
    uStack_44 = 200;
    puStack_54 = PTR_LAB_00450672_1_0058a880;
    uStack_64 = 0x58a5a5;
    piStack_58 = piVar1;
    FUN_00450408(aiStack_74);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_bounce_anim_0058a864,PTR_s_D__01_workspace_s200_ap510b_iar__0058a860,
                   PTR_s_bounce_anim_phase1_ready_cb_0058a85c,0x67,
                   PTR_s_Phase_2_animation_started__durat_0058a884,200);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__bounce_anim_Phase_2_animation_s_0058a888,
                          PTR_s__bounce_anim_Phase_2_animation_s_0058a888,200);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_bounce_anim_0058a864,PTR_s_D__01_workspace_s200_ap510b_iar__0058a860,
                   PTR_s_bounce_anim_phase1_ready_cb_0058a85c,0x4a,
                   PTR_s_phase1_ready_cb__animation_was_s_0058a870);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__bounce_anim_phase1_ready_cb__an_0058a874);
    }
  }
  return;
}

