
void text_stream_replace_and_animate(int *param_1,undefined4 param_2,undefined1 param_3)

{
  int iVar1;
  int iVar2;
  
  if (param_1 != (int *)0x0) {
    iVar1 = FUN_0044a43c(*param_1);
    param_1[3] = iVar1;
    iVar2 = param_1[3];
    iVar1 = ensure_text_capacity(param_1,param_1,param_1 + 9,iVar2 + 1);
    if (iVar1 != 0) {
      FUN_0044b5a0(*param_1,param_1[1],iVar2);
      *(undefined1 *)(*param_1 + iVar2) = 0;
      if (param_1[6] != 0) {
        (*(code *)param_1[6])(*param_1);
      }
      if (param_1[3] < param_1[4]) {
        text_stream_start_animation(param_1,param_3);
      }
    }
  }
  return;
}

