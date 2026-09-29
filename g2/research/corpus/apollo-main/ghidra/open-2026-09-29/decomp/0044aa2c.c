
void FUN_0044aa2c(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_0044aafc;
  if (*DAT_0044aafc == 0) {
    iVar2 = osMutexNew(DAT_0044ab00);
    *piVar1 = iVar2;
  }
  return;
}

