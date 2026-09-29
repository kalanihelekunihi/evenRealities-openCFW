
undefined8 even_ai_manage_char_window(uint param_1,undefined *param_2)

{
  int iVar1;
  ushort uVar2;
  int iVar3;
  short sVar4;
  
  sVar4 = 0;
  while (((iVar1 = DAT_004e64a8, 0x400 < *(ushort *)(DAT_004e64a8 + 0x1a) &&
          (1 < *(byte *)(DAT_004e64a8 + 0x18))) && (*(int *)(DAT_004e64a8 + 0x10) != 0))) {
    uVar2 = even_ai_text_width_measure();
    even_ai_dialogs_refresh();
    if (uVar2 < *(ushort *)(iVar1 + 0x1a)) {
      *(ushort *)(iVar1 + 0x1a) = *(short *)(iVar1 + 0x1a) - uVar2;
    }
    else {
      *(undefined2 *)(iVar1 + 0x1a) = 0;
    }
    sVar4 = sVar4 + 1;
  }
  if (sVar4 != 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x4ee;
      param_2 = PTR_s_Even_AI__Character_window_manage_004e6a70;
      FUN_0043d574(3,PTR_s_even_ai_ui_004e6a7c,PTR_s_D__01_workspace_s200_ap510b_iar__004e6a78,
                   PTR_s_even_ai_manage_char_window_004e6a74,0x4ee,
                   PTR_s_Even_AI__Character_window_manage_004e6a70,sVar4,
                   *(undefined2 *)(iVar1 + 0x1a));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      param_1 = (uint)*(ushort *)(iVar1 + 0x1a);
      compress_log_output(0xc800000,PTR_s__even_ai_ui_Even_AI__Character_w_004e6ae0,
                          PTR_s__even_ai_ui_Even_AI__Character_w_004e6ae0,sVar4);
    }
  }
  return CONCAT44(param_2,param_1);
}

