
undefined4 text_stream_set_text(int param_1,int param_2,int param_3,char param_4,undefined1 param_5)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar1 = 0;
  }
  else {
    if (0 < param_3) {
      *(int *)(param_1 + 8) = param_3;
    }
    iVar2 = text_stream_prepare_input(param_1,param_2,param_4);
    if (iVar2 == 0) {
      text_stream_stop_animation(param_1);
      if (param_4 == '\x01') {
        iVar3 = *(int *)(param_1 + 0x10);
        iVar2 = FUN_0044a43c(param_2);
        iVar2 = iVar2 + iVar3;
        iVar3 = ensure_text_capacity(param_1,param_1 + 4,param_1 + 0x28,iVar2 + 1);
        if (iVar3 == 0) {
          text_stream_start_pending_animation(param_1);
          return 0;
        }
        FUN_00567c80(*(undefined4 *)(param_1 + 4),param_2);
        *(int *)(param_1 + 0x10) = iVar2;
      }
      else {
        iVar2 = FUN_0044a43c(param_2);
        iVar3 = ensure_text_capacity(param_1,param_1 + 4,param_1 + 0x28,iVar2 + 1);
        if (iVar3 == 0) {
          text_stream_start_pending_animation(param_1);
          return 0;
        }
        FUN_0048d540(*(undefined4 *)(param_1 + 4),param_2);
        *(int *)(param_1 + 0x10) = iVar2;
      }
      text_stream_apply_update(param_1,param_4,param_5);
      uVar1 = text_stream_is_complete(param_1);
    }
    else {
      uVar1 = 0;
    }
  }
  return uVar1;
}

