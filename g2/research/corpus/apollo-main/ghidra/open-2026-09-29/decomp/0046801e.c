
void onboarding_process_mutex_init(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_00468c28;
  if (*DAT_00468c28 == 0) {
    iVar2 = osMutexNew(0);
    *piVar1 = iVar2;
  }
  return;
}

