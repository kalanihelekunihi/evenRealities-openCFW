
void FUN_00585ca4(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_00586394;
  if (*DAT_00586394 == 0) {
    iVar2 = osMutexNew(0);
    *piVar1 = iVar2;
  }
  return;
}

