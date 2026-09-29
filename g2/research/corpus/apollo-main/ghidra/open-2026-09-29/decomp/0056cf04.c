
int SmpScAlloc(undefined1 param_1,undefined4 param_2,int param_3)

{
  int iVar1;
  
  iVar1 = WsfBufAlloc(param_1);
  if (iVar1 == 0) {
    *(undefined1 *)(param_3 + 3) = 8;
    *(undefined1 *)(param_3 + 2) = 3;
    smpSmExecute(param_2,param_3);
  }
  return iVar1;
}

