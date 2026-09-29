
void FUN_0058a680(int param_1,int param_2,char param_3,int param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined *puVar4;
  int iStack_7c;
  undefined *puStack_78;
  undefined *puStack_6c;
  int *piStack_60;
  undefined *puStack_5c;
  undefined4 uStack_4c;
  int iStack_1c;
  
  iStack_1c = param_4;
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_bounce_anim_0058a864,PTR_s_D__01_workspace_s200_ap510b_iar__0058a860,
                   PTR_s_bounce_animation_play_0058a8ac,0x9c,PTR_s_obj_is_NULL_0058a8a8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__bounce_anim_obj_is_NULL_0058a8b0,
                          PTR_s__bounce_anim_obj_is_NULL_0058a8b0);
    }
  }
  else {
    FUN_0058a7d2(param_1);
    piVar1 = DAT_0058a86c;
    *DAT_0058a86c = param_1;
    piVar1[1] = param_2;
    *(char *)(piVar1 + 2) = param_3;
    piVar1[3] = param_4;
    if (param_3 == '\0') {
      iVar2 = piVar1[1] + -0x1e;
      puVar4 = PTR_s_TOP_TO_BOTTOM_0058a8b4;
    }
    else {
      iVar2 = piVar1[1] + 0x1e;
      puVar4 = PTR_s_BOTTOM_TO_TOP_0058a8b8;
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      puStack_78 = (undefined *)0x190;
      iStack_7c = 0x1e;
      FUN_0043d574(3,PTR_s_bounce_anim_0058a864,PTR_s_D__01_workspace_s200_ap510b_iar__0058a860,
                   PTR_s_bounce_animation_play_0058a8ac,0xb9,
                   PTR_s_Starting_bounce_animation__direc_0058a8bc,puVar4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xcc00000,PTR_s__bounce_anim_Starting_bounce_ani_0058a8c0,
                          PTR_s__bounce_anim_Starting_bounce_ani_0058a8c0,puVar4,0x1e,400);
    }
    FUN_004503d6(&iStack_7c);
    puStack_78 = PTR_FUN_0058a3fc_1_0058a8c4;
    iStack_7c = param_1;
    FUN_004506ce(&iStack_7c,piVar1[1],iVar2);
    uStack_4c = 200;
    puStack_5c = PTR_LAB_00450672_1_0058a880;
    puStack_6c = PTR_FUN_0058a408_1_0058a8c8;
    piStack_60 = piVar1;
    FUN_00450408(&iStack_7c);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_bounce_anim_0058a864,PTR_s_D__01_workspace_s200_ap510b_iar__0058a860,
                   PTR_s_bounce_animation_play_0058a8ac,199,
                   PTR_s_Phase_1_animation_started__durat_0058a8cc,200);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__bounce_anim_Phase_1_animation_s_0058a8d0,
                          PTR_s__bounce_anim_Phase_1_animation_s_0058a8d0,200);
    }
  }
  return;
}

