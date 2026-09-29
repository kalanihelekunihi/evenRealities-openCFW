
void FUN_004d9b34(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_004da5f0;
  if (*DAT_004da5f0 == 0) {
    iVar2 = osMutexNew(0);
    *piVar1 = iVar2;
  }
  return;
}

