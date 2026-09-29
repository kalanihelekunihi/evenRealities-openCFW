
undefined8 hciCmdSend(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  byte *pbVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  uStack_18 = param_3;
  uStack_14 = param_4;
  if (param_1 != 0) {
    WsfMsgEnq(DAT_0052b6b0,0);
  }
  iVar1 = DAT_0052b6b4;
  if (*(char *)(DAT_0052b6b4 + 0x1a) != '\0') {
    iVar5 = DAT_0052b6b4 + 0x10;
    pbVar2 = (byte *)WsfMsgPeek(iVar5,&uStack_18);
    if (pbVar2 != (byte *)0x0) {
      *(ushort *)(iVar1 + 0x18) = (ushort)pbVar2[1] * 0x100 + (ushort)*pbVar2;
      WsfTimerStartSec(iVar1,10);
      iVar3 = hciTrSendCmd(pbVar2);
      if (iVar3 == 1) {
        WsfMsgDeq(iVar5,&uStack_18);
        *(char *)(iVar1 + 0x1a) = *(char *)(iVar1 + 0x1a) + -1;
        WsfMsgFree(pbVar2);
        uVar4 = 1;
        goto LAB_0052aec4;
      }
    }
  }
  uVar4 = 0;
LAB_0052aec4:
  return CONCAT44(uStack_18,uVar4);
}

