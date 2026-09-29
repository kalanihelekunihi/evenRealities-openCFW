
undefined8 FUN_0058a7d2(int param_1,undefined4 param_2,undefined *param_3)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_0058a86c;
  if (param_1 != 0) {
    if (*DAT_0058a86c == param_1) {
      FUN_0043f142(param_1,DAT_0058a86c[1]);
      *piVar1 = 0;
      FUN_00450500(param_1,0);
    }
    else {
      FUN_00450500(param_1,0);
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0xe2;
      param_3 = PTR_s_Bounce_animation_stopped_for_obj_0058a8d4;
      FUN_0043d574(4,PTR_s_bounce_anim_0058a864,PTR_s_D__01_workspace_s200_ap510b_iar__0058a860,
                   PTR_s_bounce_animation_stop_0058a8d8,0xe2,
                   PTR_s_Bounce_animation_stopped_for_obj_0058a8d4,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__bounce_anim_Bounce_animation_st_0058a8dc,
                          PTR_s__bounce_anim_Bounce_animation_st_0058a8dc,param_1);
    }
  }
  return CONCAT44(param_3,param_2);
}

