
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_004ac0f8(void)

{
  int *piVar1;
  
  piVar1 = DAT_004aca98;
  if (*DAT_004aca98 != 0) {
    osTimerStop(*DAT_004aca98);
    osTimerDelete(*piVar1);
    *piVar1 = 0;
  }
  piVar1 = _DAT_004acb08;
  if (*_DAT_004acb08 != 0) {
    osTimerStop(*_DAT_004acb08);
    osTimerDelete(*piVar1);
    *piVar1 = 0;
  }
  return;
}

