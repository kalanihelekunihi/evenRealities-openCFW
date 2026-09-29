
undefined4
attcSendPrepWriteReq(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  ushort uVar2;
  
  uVar2 = *(ushort *)(*param_1 + (uint)*(byte *)(param_1 + 10) * 4);
  if (*(char *)((int)param_1 + 7) == '\x01') {
    if ((int)(uint)*(ushort *)(param_1 + 4) < (int)(uVar2 - 5)) {
      uVar2 = *(ushort *)(param_1 + 4);
    }
    else {
      uVar2 = uVar2 - 5;
    }
    iVar1 = attMsgAlloc(uVar2 + 0xd);
    if (iVar1 == 0) {
      attcReqClear(*(undefined1 *)((int)param_1 + 0x29),param_1 + 1,0x70);
      return param_4;
    }
    FUN_00439be4(iVar1,param_1[2],0xd);
    FUN_00439be4(iVar1 + 0xd,param_1[5],uVar2);
    param_1[5] = param_1[5] + (uint)uVar2;
    *(ushort *)(param_1 + 4) = (short)param_1[4] - uVar2;
  }
  else {
    uVar2 = *(ushort *)(param_1 + 4);
    iVar1 = param_1[2];
    param_1[2] = 0;
  }
  *(char *)(iVar1 + 0xb) = (char)*(undefined2 *)((int)param_1 + 0x12);
  *(char *)(iVar1 + 0xc) = (char)((ushort)*(undefined2 *)((int)param_1 + 0x12) >> 8);
  *(ushort *)((int)param_1 + 0x12) = uVar2 + *(short *)((int)param_1 + 0x12);
  *(undefined1 *)((int)param_1 + 0x22) = 0x14;
  WsfTimerStartSec(param_1 + 6,*(undefined1 *)(*DAT_00531b9c + 6));
  attL2cDataReq(*param_1,*(undefined1 *)((int)param_1 + 0xe),uVar2 + 5,iVar1);
  return param_4;
}

