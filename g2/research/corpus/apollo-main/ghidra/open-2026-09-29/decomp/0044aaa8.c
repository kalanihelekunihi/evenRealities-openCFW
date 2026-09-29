
undefined4 FUN_0044aaa8(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined1 auStack_30 [12];
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  service_time_current_calendar_get(auStack_30);
  uVar2 = osKernelGetTickCount();
  uVar1 = DAT_0044ab08;
  FUN_0044b728(DAT_0044ab08,0x1c,DAT_0044ab0c,local_24,local_20,local_1c,local_18,local_14,local_10,
               uVar2);
  return uVar1;
}

