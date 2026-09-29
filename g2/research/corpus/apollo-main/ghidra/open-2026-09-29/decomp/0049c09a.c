
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0049c09a(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = _DAT_0049cb14;
  if (*_DAT_0049cb14 == 0) {
    iVar2 = osMutexNew(0);
    *piVar1 = iVar2;
  }
  return;
}

