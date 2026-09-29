
undefined8 wsfOsDispatcher(undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  byte bVar4;
  uint uVar5;
  undefined4 uStack_18;
  uint uStack_14;
  
  iVar3 = DAT_0052bac4;
  uStack_14 = param_4;
  WsfTimerUpdateTicks();
  while (*(char *)(iVar3 + 0x3c) != '\0') {
    WsfCsEnter();
    uVar5 = (uint)*(byte *)(iVar3 + 0x3c);
    *(undefined1 *)(iVar3 + 0x3c) = 0;
    WsfCsExit();
    if ((int)(uVar5 << 0x1f) < 0) {
      while (iVar2 = WsfMsgDeq(iVar3 + 0x34,&uStack_14), iVar2 != 0) {
        (**(code **)(iVar3 + (uStack_14 & 0xff) * 4))(0,iVar2);
        WsfMsgFree(iVar2);
      }
    }
    if ((int)(uVar5 << 0x1e) < 0) {
      while (iVar2 = WsfTimerServiceExpired(0), iVar2 != 0) {
        (**(code **)(iVar3 + (uint)*(byte *)(iVar2 + 0xc) * 4))(0,iVar2 + 8);
      }
    }
    if ((int)(uVar5 << 0x1d) < 0) {
      for (bVar4 = 0; bVar4 < 10; bVar4 = bVar4 + 1) {
        if ((*(char *)((uint)bVar4 + iVar3 + 0x28) != '\0') &&
           (*(int *)(iVar3 + (uint)bVar4 * 4) != 0)) {
          WsfCsEnter();
          uVar1 = *(undefined1 *)((uint)bVar4 + iVar3 + 0x28);
          *(undefined1 *)((uint)bVar4 + iVar3 + 0x28) = 0;
          WsfCsExit();
          (**(code **)(iVar3 + (uint)bVar4 * 4))(uVar1,0);
        }
      }
    }
  }
  WsfTimerUpdateTicks();
  iVar3 = wsfOsReadyToSleep();
  uStack_18 = param_3;
  if (iVar3 != 0) {
    uStack_18 = 0xffffffff;
    FUN_0047ebf8(*DAT_0052babc,1,1,0);
  }
  return CONCAT44(uStack_14,uStack_18);
}

