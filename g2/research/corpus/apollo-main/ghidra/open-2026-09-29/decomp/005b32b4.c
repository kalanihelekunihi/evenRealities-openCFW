
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_005b32b4(undefined4 param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar2 = _DAT_005b3514;
  iVar1 = FUN_0044dce2(*(undefined4 *)(_DAT_005b3514 + 0x20),0);
  if (iVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x208;
      FUN_0043d574(1,PTR_s_conversate_ui_005b3528,PTR_s_D__01_workspace_s200_ap510b_iar__005b3524,
                   PTR_s_conversate_ui_action_transcribe__005b3564,0x208,
                   PTR_s_transcribe_label_is_NULL_005b3560);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__conversate_ui_transcribe_label_i_005b3568,
                          PTR_s__conversate_ui_transcribe_label_i_005b3568);
    }
  }
  else {
    uVar3 = func_0x005b4364();
    FUN_0049942e(iVar1,uVar3);
    iVar4 = FUN_0043fdda(*(undefined4 *)(iVar2 + 0x20));
    iVar1 = FUN_0043fdda(iVar1);
    FUN_0044ea04(*(undefined4 *)(iVar2 + 0x20),iVar1 - iVar4,0);
  }
  return (ulonglong)param_3 << 0x20;
}

