
longlong translate_ui_0059e498(undefined4 param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  iVar1 = DAT_0059e5cc;
  if (*(int *)(DAT_0059e5cc + 8) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x28a;
      FUN_0043d574(2,DAT_0059e640,DAT_0059e63c,PTR_s_translate_ui_action_pause_0059e6b8,0x28a,
                   PTR_s_gif_animation_is_NULL_or_invalid_0059e6b4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__translate_ui_gif_animation_is_N_0059e6bc,
                          PTR_s__translate_ui_gif_animation_is_N_0059e6bc);
    }
  }
  else {
    FUN_0058c836(*(undefined4 *)(DAT_0059e5cc + 8));
    FUN_0043ded4(*(undefined4 *)(iVar1 + 8),1);
    iVar2 = FUN_0044dce2(*(undefined4 *)(iVar1 + 4),2);
    if (iVar2 == 0) {
      uVar3 = FUN_00498668(*(undefined4 *)(iVar1 + 4));
      FUN_00498680(uVar3,PTR_DAT_0059e6c0);
      uVar4 = FUN_0044104c(0);
      FUN_0044127e(uVar3,uVar4,0);
      FUN_0044129e(uVar3,0xff,0);
      FUN_004413ce(uVar3,0xff,0);
      FUN_0043f4c0(uVar3,0x3fffffff);
      FUN_0043f6b8(uVar3,7,0,0);
    }
  }
  return (ulonglong)param_3 << 0x20;
}

