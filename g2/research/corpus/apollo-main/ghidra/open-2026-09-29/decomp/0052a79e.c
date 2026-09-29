
undefined8 hciCoreTxReady(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  byte *pbVar4;
  int iVar5;
  byte bVar6;
  int iVar7;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  iVar7 = DAT_0052ae14;
  bVar6 = 0;
  uStack_20 = param_3;
  uStack_1c = param_4;
  if ((param_1 != '\0') &&
     (*(char *)(DAT_0052ae14 + 0x82) = param_1 + *(char *)(DAT_0052ae14 + 0x82),
     *(byte *)(iVar7 + 0x83) < *(byte *)(iVar7 + 0x82))) {
    *(undefined1 *)(iVar7 + 0x82) = *(undefined1 *)(iVar7 + 0x83);
  }
  while (iVar7 = DAT_0052ae14, *(char *)(DAT_0052ae14 + 0x82) != '\0') {
    iVar3 = hciCoreTxAclContinue(0);
    if (iVar3 == 0) {
      iVar7 = iVar7 + 0x70;
      pbVar4 = (byte *)WsfMsgPeek(iVar7,&uStack_20);
      if (pbVar4 == (byte *)0x0) break;
      bVar1 = pbVar4[2];
      bVar2 = pbVar4[3];
      iVar3 = hciCoreConnByHandle((uint)pbVar4[1] * 0x100 + (uint)*pbVar4);
      if (iVar3 == 0) {
        WsfMsgDeq(iVar7,&uStack_20);
        WsfMsgFree();
      }
      else {
        iVar5 = hciCoreTxAclStart(iVar3,(uint)bVar2 * 0x100 + (uint)bVar1,pbVar4);
        if (iVar5 != 1) break;
        WsfMsgDeq(iVar7,&uStack_20);
        hciCoreTxAclComplete(iVar3,pbVar4);
        bVar6 = 1;
      }
    }
  }
  return CONCAT44(uStack_20,(uint)bVar6);
}

