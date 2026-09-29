
undefined8 FUN_00479418(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  byte bVar4;
  byte bVar5;
  int iVar6;
  byte bVar7;
  
  piVar1 = DAT_00479b24;
  iVar6 = *DAT_00479b24;
  bVar4 = 0;
  bVar5 = 0;
  for (bVar7 = 0; bVar7 < 10; bVar7 = bVar7 + 1) {
    if (((*(char *)(iVar6 + 0x2f) != '\0') && (*(char *)(iVar6 + 0x30) != '\0')) &&
       (iVar2 = FUN_004751c8(iVar6 + 7,DAT_00479b28,0x10), iVar2 != 0)) {
      bVar5 = bVar5 + 1;
    }
    iVar6 = iVar6 + 200;
  }
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    param_1 = 0x115;
    param_2 = DAT_00479b2c;
    FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_00479b30,0x115,DAT_00479b2c,bVar5,param_4);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00479b34,DAT_00479b34,bVar5);
  }
  iVar6 = *piVar1;
  for (bVar7 = 0; bVar7 < 10; bVar7 = bVar7 + 1) {
    if (((*(char *)(iVar6 + 0x2f) != '\0') && (*(char *)(iVar6 + 0x30) != '\0')) &&
       (iVar2 = FUN_004751c8(iVar6 + 7,DAT_00479b28,0x10), iVar2 != 0)) {
      *(byte *)(iVar6 + 0x2e) = *(byte *)(iVar6 + 0x2e) | 4;
      uVar3 = DmSecGetLocalIrk();
      param_2 = 0;
      param_1 = (uint)((uint)bVar4 == bVar5 - 1);
      DmPrivAddDevToResList(*(undefined1 *)(iVar6 + 0x1d),iVar6 + 0x17,iVar6 + 7,uVar3);
      bVar4 = bVar4 + 1;
    }
    iVar6 = iVar6 + 200;
  }
  if (bVar4 != 0) {
    DmPrivSetAddrResEnable(1);
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      param_1 = 0x130;
      param_2 = DAT_00479b38;
      FUN_0043d574(4,DAT_00479574,DAT_00479570,DAT_00479b30);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00479b3c,DAT_00479b3c);
    }
  }
  return CONCAT44(param_2,param_1);
}

