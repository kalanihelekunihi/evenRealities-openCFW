
void device_mgr_fn_004c6a9e(void)

{
  int iVar1;
  undefined1 auStack_30 [40];
  
  service_time_current_calendar_get(auStack_30);
  iVar1 = DAT_004c6ce4;
  FUN_00439c04(DAT_004c6ce4 + 0x58,auStack_30,0x28);
  if (*DAT_004c6ce8 == '\0') {
    FUN_00439c04(iVar1 + 0x80,auStack_30,0x28);
  }
  SVC_NvdbWriteSysData(7,iVar1 + 0x58);
  return;
}

