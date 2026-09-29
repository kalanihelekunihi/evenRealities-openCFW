
undefined8 SmpScGetCancelMsgWithReattempt(byte param_1,ushort *param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  ushort *puVar3;
  undefined4 uVar4;
  
  puVar3 = param_2;
  uVar4 = param_3;
  iVar1 = smpCcbByConnId(param_1);
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056d82c,&DAT_0056d2fc,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056d82c,DAT_0056d83c,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056d82c,DAT_0056d82c,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&LAB_0056d300,&DAT_0056d474,3), iVar2 != 0)) {
            WsfTrace(DAT_0056d82c,DAT_0056d830,*(undefined1 *)(iVar1 + 0x42));
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            puVar3 = (ushort *)0x248;
            uVar4 = DAT_0056d830;
            FUN_0043d574(4,&LAB_0056d300,DAT_0056d838,DAT_0056d834,0x248,DAT_0056d830,
                         *(undefined1 *)(iVar1 + 0x42));
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          puVar3 = (ushort *)0x248;
          uVar4 = DAT_0056d830;
          FUN_0043d574(3,&LAB_0056d300,DAT_0056d838,DAT_0056d834,0x248,DAT_0056d830,
                       *(undefined1 *)(iVar1 + 0x42));
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puVar3 = (ushort *)0x248;
        uVar4 = DAT_0056d830;
        FUN_0043d574(2,&LAB_0056d300,DAT_0056d838,DAT_0056d834,0x248,DAT_0056d830,
                     *(undefined1 *)(iVar1 + 0x42));
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      puVar3 = (ushort *)0x248;
      uVar4 = DAT_0056d830;
      FUN_0043d574(1,&LAB_0056d300,DAT_0056d838,DAT_0056d834,0x248,DAT_0056d830,
                   *(undefined1 *)(iVar1 + 0x42));
    }
  }
  *(char *)(iVar1 + 0x42) = *(char *)(iVar1 + 0x42) + '\x01';
  *param_2 = (ushort)param_1;
  *(char *)((int)param_2 + 3) = (char)param_3;
  SmpDbPairingFailed(param_1);
  if (*(char *)(iVar1 + 0x42) == *(char *)(*DAT_0056d840 + 7)) {
    *(undefined1 *)(param_2 + 1) = 0xd;
  }
  else {
    *(undefined1 *)(param_2 + 1) = 3;
  }
  return CONCAT44(uVar4,puVar3);
}

