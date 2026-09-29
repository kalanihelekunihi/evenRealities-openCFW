
void dashboard_watchface_manager_deinit(void)

{
  int *piVar1;
  
  piVar1 = DAT_005007fc;
  if ((*DAT_005007fc != 0) && (*(int *)(*DAT_005007fc + 4) != 0)) {
    (**(code **)(*DAT_005007fc + 4))();
  }
  *piVar1 = 0;
  return;
}

