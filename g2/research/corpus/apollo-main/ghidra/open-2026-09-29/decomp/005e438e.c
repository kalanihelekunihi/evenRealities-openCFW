
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

bool terminal_action_lock(void)

{
  int *piVar1;
  int iVar2;
  bool bVar3;
  
  piVar1 = _DAT_005e4768;
  if ((*_DAT_005e4768 == 0) && (iVar2 = terminal_action_mutex_init_internal(), iVar2 != 0)) {
    bVar3 = false;
  }
  else {
    iVar2 = osMutexAcquire(*piVar1,0xffffffff);
    bVar3 = iVar2 == 0;
  }
  return bVar3;
}

