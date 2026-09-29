
int service_time_current_epoch_get(void)

{
  int iVar1;
  undefined1 auStack_30 [40];
  
  FUN_0047ef10(auStack_30);
  iVar1 = service_time_calendar_to_epoch(auStack_30);
  return (short)*(char *)(*DAT_0044a40c + 8) * 900 + iVar1;
}

