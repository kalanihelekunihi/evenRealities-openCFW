
ushort * attcSendMsg(byte param_1,ushort param_2,char param_3,ushort *param_4,char param_5)

{
  ushort uVar1;
  int *piVar2;
  ushort *puVar3;
  ushort uVar4;
  byte bVar5;
  
  WsfTaskLock();
  piVar2 = (int *)attcCcbByConnId(param_1,0);
  if (piVar2 == (int *)0x0) {
    uVar4 = 0;
    bVar5 = 0;
  }
  else {
    uVar4 = *(ushort *)*piVar2;
    bVar5 = (byte)(((uint)*(byte *)(*piVar2 + 2) << 0x1d) >> 0x1f);
  }
  WsfTaskUnlock();
  if (uVar4 != 0) {
    if (bVar5 == 0) {
      uVar1 = 0;
      if (param_4 != (ushort *)0x0) {
        if (param_3 == '\v') {
          if (param_5 == '\0') {
            uVar1 = **(short **)param_4 + 5;
          }
        }
        else {
          uVar1 = *param_4;
        }
      }
      if (uVar4 < uVar1) {
        attcExecCallback(param_1,param_3,param_2,0x77);
      }
      else {
        puVar3 = (ushort *)WsfMsgAlloc(0xc);
        if (puVar3 != (ushort *)0x0) {
          *puVar3 = (ushort)param_1;
          *(char *)((int)puVar3 + 3) = param_5;
          *(char *)(puVar3 + 1) = param_3;
          *(ushort **)(puVar3 + 2) = param_4;
          puVar3[4] = param_2;
          *(undefined1 *)(puVar3 + 5) = 0;
          WsfMsgSend(*(undefined1 *)(DAT_004b599c + 0x60),puVar3);
          return param_4;
        }
      }
    }
    else {
      attcExecCallback(param_1,param_3,param_2,0x71);
    }
  }
  if (param_4 != (ushort *)0x0) {
    WsfMsgFree(param_4);
  }
  return param_4;
}

