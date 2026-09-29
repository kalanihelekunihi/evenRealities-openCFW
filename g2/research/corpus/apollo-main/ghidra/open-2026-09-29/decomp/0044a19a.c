
void service_time_current_calendar_get(undefined4 param_1)

{
  int iVar1;
  undefined1 auStack_30 [40];
  
  FUN_0047ef10(auStack_30);
  iVar1 = service_time_calendar_to_epoch(auStack_30);
  service_time_epoch_to_calendar_configured
            ((short)*(char *)(*DAT_0044a40c + 8) * 900 + iVar1,param_1);
  return;
}

