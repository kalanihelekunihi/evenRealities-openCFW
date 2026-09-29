
void service_time_sync_callback(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_30 [40];
  
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    FUN_0047ef10(auStack_30);
    uVar2 = service_time_calendar_to_epoch(auStack_30);
    SVC_SystemTimeSync(uVar2,(int)*(char *)(*DAT_0044a40c + 8));
  }
  uVar2 = DAT_0044a438;
  fw_event_loop_remove_delayed(DAT_0044a438);
  fw_event_loop_push_delayed(uVar2,0,0);
  return;
}

