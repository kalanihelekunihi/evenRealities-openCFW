
undefined4 translate_ui_0059dfa0(undefined4 param_1,int param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  if (param_2 == 1) {
    FUN_0059e9e2();
  }
  else {
    uVar1 = osKernelGetTickCount();
    *(undefined4 *)(DAT_0059e26c + 0x28) = uVar1;
  }
  uVar1 = func_0x0059ea10();
  uVar2 = func_0x0059ea14();
  iVar3 = DAT_0059e26c;
  if ((*(int *)(DAT_0059e26c + 0x14) == 0) || (*(int *)(DAT_0059e26c + 0x1c) == 0)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0059e640,DAT_0059e63c,PTR_s_translate_ui_action_text_update_0059e64c,0x1e6,
                   PTR_s_src_text_label_or_dst_text_label_0059e648);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__translate_ui_src_text_label_or_d_0059e650);
    }
    uVar1 = 0xffffffff;
  }
  else {
    FUN_0049942e(*(undefined4 *)(DAT_0059e26c + 0x14),uVar1);
    FUN_0049942e(*(undefined4 *)(iVar3 + 0x1c),uVar2);
    FUN_0043f66c(*(undefined4 *)(iVar3 + 0x18));
    FUN_0043f6d6(*(undefined4 *)(iVar3 + 0x10),*(undefined4 *)(iVar3 + 0x18),0xb,0,0xfffffff4);
    iVar4 = FUN_0043fdda(*(undefined4 *)(iVar3 + 0x10));
    iVar5 = FUN_0043fdda(*(undefined4 *)(iVar3 + 0x14));
    iVar5 = iVar5 - iVar4;
    iVar4 = FUN_0043fdda(*(undefined4 *)(iVar3 + 0x18));
    iVar6 = FUN_0043fdda(*(undefined4 *)(iVar3 + 0x1c));
    iVar6 = iVar6 - iVar4;
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0059e640,DAT_0059e63c,PTR_s_translate_ui_action_text_update_0059e64c,0x1f8,
                   PTR_s_src_target_y___d__dst_target_y____0059e654,iVar5,iVar6);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__translate_ui_src_target_y___d__d_0059e658,
                          PTR_s__translate_ui_src_target_y___d__d_0059e658,iVar5,iVar6);
    }
    FUN_0044ea04(*(undefined4 *)(iVar3 + 0x10),iVar5,0);
    FUN_0044ea04(*(undefined4 *)(iVar3 + 0x18),iVar6,0);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0059e640,DAT_0059e63c,PTR_s_translate_ui_action_text_update_0059e64c,0x1fd,
                   PTR_s_Text_updated_0059e65c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__translate_ui_Text_updated_0059e660,
                          PTR_s__translate_ui_Text_updated_0059e660);
    }
    uVar1 = 0;
  }
  return uVar1;
}

