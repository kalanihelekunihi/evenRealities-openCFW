
void FUN_00463eee(int *param_1)

{
  int iVar1;
  
  if (param_1 != (int *)0x0) {
    *(undefined1 *)(param_1 + 6) = 0;
    *(undefined1 *)((int)param_1 + 0x1b) = 0;
    param_1[3] = 0;
    param_1[5] = 0;
    *(undefined1 *)((int)param_1 + 0x1a) = 1;
    if ((((param_1[1] != 0) && (*(int *)param_1[1] != 0)) && (*param_1 != 0)) &&
       (iVar1 = FUN_0043e2ea(*param_1), iVar1 != 0)) {
      FUN_00498680(*param_1,*(undefined4 *)param_1[1]);
    }
  }
  return;
}

