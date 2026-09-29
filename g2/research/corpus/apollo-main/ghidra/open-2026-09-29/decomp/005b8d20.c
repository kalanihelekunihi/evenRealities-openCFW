
void FUN_005b8d20(int *param_1)

{
  int iVar1;
  
  if ((param_1 != (int *)0x0) && (*param_1 != 0)) {
    if ((char)param_1[2] == '\x01') {
      iVar1 = FUN_0050f810(*(undefined2 *)(DAT_005b8d78 + 0x2a));
      if (iVar1 != 0) {
        FUN_00498680(*param_1);
      }
    }
    else {
      iVar1 = FUN_005b89f0((char)param_1[2]);
      if (iVar1 != 0) {
        FUN_00498680(*param_1,iVar1);
      }
    }
  }
  return;
}

