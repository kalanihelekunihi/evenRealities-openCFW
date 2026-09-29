
undefined4
even_ai_dialog_node_apply(int *param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 != (int *)0x0) {
    even_ai_node_stream_state_update(param_1);
    if (*param_1 != 0) {
      if ((param_2 != '\0') && (iVar1 = FUN_0043e2ea(*param_1), iVar1 != 0)) {
        FUN_0044d7b8(*param_1);
      }
      *param_1 = 0;
    }
    if (param_1[1] != 0) {
      if ((param_2 != '\0') && (iVar1 = FUN_0043e2ea(param_1[1]), iVar1 != 0)) {
        FUN_0044d7b8(param_1[1]);
      }
      param_1[1] = 0;
      param_1[2] = 0;
      param_1[3] = 0;
      param_1[4] = 0;
    }
    FUN_0043c0e4(param_1,0x24,0);
  }
  return param_4;
}

