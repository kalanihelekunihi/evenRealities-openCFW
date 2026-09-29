
undefined4 text_stream_apply_update(int *param_1,byte param_2,undefined1 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  if (param_1 != (int *)0x0) {
    text_stream_stop_animation(param_1);
    if ((param_1[1] == 0) || (param_1[4] == 0)) {
      if (*param_1 != 0) {
        *(undefined1 *)*param_1 = 0;
      }
      param_1[3] = 0;
      if (param_1[6] != 0) {
        (*(code *)param_1[6])(*param_1);
      }
    }
    else if (param_2 == 0) {
      uVar1 = FUN_0044a43c(*param_1);
      uVar4 = param_1[4];
      if (uVar1 < uVar4) {
        uVar3 = text_stream_common_prefix_length(*param_1,param_1[1]);
        if ((uVar3 == uVar1) && (uVar1 < uVar4)) {
          *(undefined1 *)(param_1 + 0xb) = 1;
          text_stream_animate_mode(param_1,param_3);
        }
        else {
          *(undefined1 *)(param_1 + 0xb) = 0;
          text_stream_replace_and_animate(param_1,0,param_3);
        }
      }
      else {
        iVar2 = ensure_text_capacity(param_1,param_1,param_1 + 9,uVar4 + 1);
        if (iVar2 != 0) {
          FUN_0048d540(*param_1,param_1[1]);
          param_1[3] = uVar4;
          if (param_1[6] != 0) {
            (*(code *)param_1[6])(*param_1);
          }
        }
      }
    }
    else if (param_2 == 2) {
      *(undefined1 *)(param_1 + 0xb) = 0;
      text_stream_replace_and_animate(param_1,0,param_3);
    }
    else if (param_2 < 2) {
      *(undefined1 *)(param_1 + 0xb) = 1;
      text_stream_animate_mode(param_1,param_3);
    }
  }
  return param_4;
}

