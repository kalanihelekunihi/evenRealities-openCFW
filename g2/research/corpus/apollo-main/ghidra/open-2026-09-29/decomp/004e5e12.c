
undefined4 even_ai_scroll_by_delta(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  
  iVar2 = even_ai_scroll_needed();
  if (iVar2 != 0) {
    service_even_ai_fn_00498310(1);
    even_ai_common_timer_mgr_deinit();
    pcVar1 = DAT_004e6550;
    if (((*DAT_004e6550 == '\0') || (*DAT_004e6550 == '\x01')) &&
       (iVar3 = even_ai_dialog_height_exceeds_window(), iVar2 = DAT_004e64a8, iVar3 != 0)) {
      iVar3 = FUN_0044e498(*(undefined4 *)(DAT_004e64a8 + 8));
      if (param_1 < 1) {
        iVar4 = FUN_005546be(*(undefined4 *)(iVar2 + 8),-param_2,param_3,0x1c);
      }
      else {
        iVar4 = FUN_005546be(*(undefined4 *)(iVar2 + 8),param_2,param_3,0x1c);
      }
      if (iVar4 != iVar3) {
        *pcVar1 = '\x01';
        if (param_2 < 3) {
          uVar5 = 100;
        }
        else {
          uVar5 = 200;
        }
        even_ai_scroll_to(*(undefined4 *)(iVar2 + 8),iVar4,uVar5);
      }
    }
  }
  return param_4;
}

