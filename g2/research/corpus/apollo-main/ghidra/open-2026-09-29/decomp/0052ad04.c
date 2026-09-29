
undefined4 HciSendAclData(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  ushort uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar6 = (uint)param_1[1] * 0x100 + (uint)*param_1;
  bVar1 = param_1[2];
  bVar2 = param_1[3];
  iVar5 = hciCoreConnByHandle(iVar6);
  iVar3 = DAT_0052ae14;
  if (iVar5 == 0) {
    WsfMsgFree(param_1);
  }
  else {
    iVar7 = DAT_0052ae14 + 0x70;
    WsfMsgEnq(iVar7,0,param_1);
    iVar7 = WsfQueueCount(iVar7);
    if ((iVar7 == 1) && (*(char *)(iVar3 + 0x82) != '\0')) {
      hciCoreTxReady(0);
    }
    uVar4 = HciGetBufSize();
    *(char *)(iVar5 + 0x18) =
         (char)((int)((uint)bVar2 * 0x100 + (uint)bVar1 + -1) / (int)(uint)uVar4) +
         *(char *)(iVar5 + 0x18) + '\x01';
    if ((*(byte *)(iVar3 + 0x80) <= *(byte *)(iVar5 + 0x18)) && (*(char *)(iVar5 + 0x17) == '\0')) {
      *(undefined1 *)(iVar5 + 0x17) = 1;
      (**(code **)(DAT_0052ae18 + 0x14))(iVar6,1);
    }
  }
  return param_4;
}

