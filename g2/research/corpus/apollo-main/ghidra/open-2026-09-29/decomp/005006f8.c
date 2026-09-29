
undefined4 dashboard_watchface_manager_call_1c(void)

{
  undefined4 unaff_r7;
  
  if ((*DAT_005007fc != 0) && (*(int *)(*DAT_005007fc + 0x1c) != 0)) {
    (**(code **)(*DAT_005007fc + 0x1c))();
  }
  return unaff_r7;
}

