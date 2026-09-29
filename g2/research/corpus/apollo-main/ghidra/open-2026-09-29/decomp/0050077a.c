
undefined4 dashboard_watchface_manager_call_24(undefined4 param_1,undefined1 param_2)

{
  undefined4 unaff_r7;
  
  if ((*DAT_005007fc != 0) && (*(int *)(*DAT_005007fc + 0x24) != 0)) {
    (**(code **)(*DAT_005007fc + 0x24))(param_1,param_2);
  }
  return unaff_r7;
}

