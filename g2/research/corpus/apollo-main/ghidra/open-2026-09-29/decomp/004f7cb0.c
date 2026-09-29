
undefined8 FUN_004f7cb0(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  ushort *puVar1;
  int iVar2;
  int iVar3;
  bool bVar4;
  undefined8 uVar5;
  int iVar6;
  
  iVar2 = DAT_004f8638;
  puVar1 = DAT_004f8628;
  iVar6 = param_1;
  if ((param_1 < 0) || ((int)(uint)*DAT_004f8628 <= param_1)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      iVar6 = 0xac1;
      param_2 = DAT_004f862c;
      param_3 = param_1;
      FUN_0043d574(2,DAT_004f81e0,DAT_004f81dc,DAT_004f8630,0xac1,DAT_004f862c,param_1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004f8634,DAT_004f8634,param_1,iVar6,param_2,param_3);
    }
  }
  else if ((*(int *)(DAT_004f8638 + param_1 * 0x10) == 0) ||
          (*(int *)(param_1 * 0x10 + DAT_004f8638 + 4) == 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      iVar6 = 0xac7;
      param_2 = DAT_004f863c;
      FUN_0043d574(2,DAT_004f81e0,DAT_004f81dc,DAT_004f8630,0xac7,DAT_004f863c,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004f8640,DAT_004f8640,param_1);
    }
  }
  else {
    bVar4 = *(char *)((int)DAT_004f8628 + param_1 * 0x128 + 0x129) == '\0';
    quicklist_lock_storage();
    *(bool *)((int)puVar1 + param_1 * 0x128 + 0x129) = bVar4;
    quicklist_unlock_storage();
    if (bVar4) {
      FUN_00498680(*(undefined4 *)(param_1 * 0x10 + iVar2 + 4),DAT_004f8874);
      FUN_00441488(*(undefined4 *)(iVar2 + param_1 * 0x10),0x30,0);
      iVar3 = *(int *)(puVar1 + param_1 * 0x94 + 0x8a);
      uVar5 = service_time_rtc_refresh();
      FUN_004f658c(iVar3,(int)((ulonglong)uVar5 >> 0x20),(int)uVar5,0);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        iVar6 = 0xade;
        param_2 = DAT_004f88a8;
        FUN_0043d574(4,DAT_004f81e0,DAT_004f81dc,DAT_004f8630,0xade,DAT_004f88a8,param_1,iVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004f88ac,DAT_004f88ac,param_1);
        iVar6 = iVar3;
      }
    }
    else {
      FUN_00498680(*(undefined4 *)(param_1 * 0x10 + iVar2 + 4),DAT_004f88b0);
      FUN_00441488(*(undefined4 *)(iVar2 + param_1 * 0x10),0xff,0);
      iVar3 = *(int *)(puVar1 + param_1 * 0x94 + 0x8a);
      FUN_004f6664(iVar3);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        iVar6 = 0xae8;
        param_2 = DAT_004f88b4;
        FUN_0043d574(4,DAT_004f81e0,DAT_004f81dc,DAT_004f8630,0xae8,DAT_004f88b4,param_1,iVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004f88b8,DAT_004f88b8,param_1);
        iVar6 = iVar3;
      }
    }
  }
  return CONCAT44(param_2,iVar6);
}

