
void attcSendContinuingReq(undefined4 *param_1)

{
  undefined2 *puVar1;
  
  if (*(char *)((int)param_1 + 7) == '\x01') {
    puVar1 = (undefined2 *)attMsgAlloc(*(short *)param_1[2] + 8);
    if (puVar1 == (undefined2 *)0x0) {
      attcReqClear(*(undefined1 *)((int)param_1 + 0x29),param_1 + 1,0x70);
      return;
    }
    FUN_00439be4(puVar1,param_1[2],*(ushort *)param_1[2] + 8);
  }
  else {
    puVar1 = (undefined2 *)param_1[2];
    param_1[2] = 0;
  }
  if (*(char *)((int)param_1 + 6) == '\x06') {
    *(char *)((int)puVar1 + 0xb) = (char)*(undefined2 *)((int)param_1 + 0x12);
    *(char *)(puVar1 + 6) = (char)((ushort)*(undefined2 *)((int)param_1 + 0x12) >> 8);
  }
  else {
    *(char *)((int)puVar1 + 9) = (char)*(undefined2 *)((int)param_1 + 0x12);
    *(char *)(puVar1 + 5) = (char)((ushort)*(undefined2 *)((int)param_1 + 0x12) >> 8);
    *(char *)((int)puVar1 + 0xb) = (char)*(undefined2 *)(param_1 + 5);
    *(char *)(puVar1 + 6) = (char)((ushort)*(undefined2 *)(param_1 + 5) >> 8);
  }
  *(undefined1 *)((int)param_1 + 0x22) = 0x14;
  WsfTimerStartSec(param_1 + 6,*(undefined1 *)(*DAT_00531aac + 6));
  attL2cDataReq(*param_1,*(undefined1 *)((int)param_1 + 0xe),*puVar1,puVar1);
  return;
}

