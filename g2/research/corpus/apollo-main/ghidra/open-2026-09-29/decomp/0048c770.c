
undefined4 FUN_0048c770(int param_1,char param_2,int *param_3)

{
  undefined4 uVar1;
  
  if (param_2 == '\0') {
    *param_3 = *param_3 + 1;
    if (*param_3 < (int)(uint)*(ushort *)(*(int *)(param_1 + 8) + 0x30)) {
      uVar1 = *(undefined4 *)(**(int **)(param_1 + 8) + *param_3 * 4);
    }
    else {
      uVar1 = 0;
    }
  }
  else {
    *param_3 = *param_3 + -1;
    if (*param_3 < 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = *(undefined4 *)(**(int **)(param_1 + 8) + *param_3 * 4);
    }
  }
  return uVar1;
}

