
undefined4 dashboard_watchface_manager_call_10(void)

{
  undefined4 in_r3;
  
  if ((*DAT_005007fc != 0) && (*(int *)(*DAT_005007fc + 0x10) != 0)) {
    (**(code **)(*DAT_005007fc + 0x10))();
  }
  return in_r3;
}

