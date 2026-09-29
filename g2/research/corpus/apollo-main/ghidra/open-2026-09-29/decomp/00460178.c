
void FUN_00460178(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_0046061c;
  if (*DAT_0046061c == 0) {
    iVar2 = osMutexNew(0);
    *piVar1 = iVar2;
  }
  return;
}

