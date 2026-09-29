
void FUN_004ac130(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_004aca98;
  if ((*DAT_004aca98 != 0) && (iVar2 = osTimerIsRunning(*DAT_004aca98), iVar2 != 0)) {
    osTimerStop(*piVar1);
  }
  FUN_004abfac(1);
  return;
}

