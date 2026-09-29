
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
even_ai_show_listening_text
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  iVar2 = DAT_004e64a8;
  uStack_10 = param_3;
  uStack_c = param_4;
  if ((*(int *)(DAT_004e64a8 + 0xc) == 0) ||
     (iVar1 = FUN_0043e2ea(*(undefined4 *)(DAT_004e64a8 + 0xc)), iVar1 == 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_c = PTR_s_label_listening_is_NULL_004e6ae4;
      uStack_10 = 0x549;
      FUN_0043d574(1,PTR_s_even_ai_ui_004e6a7c,PTR_s_D__01_workspace_s200_ap510b_iar__004e6a78,
                   PTR_s_even_ai_show_listening_text_004e6ae8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,_DAT_004e6c18,_DAT_004e6c18);
    }
  }
  else {
    FUN_0043dfa4(*(undefined4 *)(iVar2 + 0xc),1);
  }
  return CONCAT44(uStack_c,uStack_10);
}

