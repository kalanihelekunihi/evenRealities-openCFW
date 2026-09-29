
undefined4 dashboard_watchface_manager_call_2c(undefined1 param_1)

{
  undefined4 unaff_r7;
  
  if ((*DAT_005007fc != 0) && (*(int *)(*DAT_005007fc + 0x2c) != 0)) {
    (**(code **)(*DAT_005007fc + 0x2c))(param_1);
  }
  return unaff_r7;
}

