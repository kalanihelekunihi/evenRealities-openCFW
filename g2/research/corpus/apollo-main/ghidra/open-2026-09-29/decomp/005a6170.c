
undefined8 attsProcExecWriteReq(int param_1,uint param_2,int param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  uint local_20;
  int iStack_1c;
  undefined4 uStack_18;
  
  iVar3 = DAT_005a6258;
  bVar1 = 0;
  iStack_1c = param_3;
  uStack_18 = param_4;
  if (*(char *)(param_3 + 9) == '\0') {
    attsClearPrepWrites(param_1);
  }
  else if (*(char *)(param_3 + 9) == '\x01') {
    for (puVar4 = *(undefined4 **)(DAT_005a6258 + (uint)*(byte *)(param_1 + 0x24) * 8 + 0x238);
        puVar4 != (undefined4 *)0x0; puVar4 = (undefined4 *)*puVar4) {
      iVar2 = attsFindByHandle(*(undefined2 *)((int)puVar4 + 6),&iStack_1c);
      if (iVar2 != 0) {
        if (*(ushort *)(iVar2 + 0xc) < *(ushort *)(puVar4 + 2)) {
          bVar1 = 7;
        }
        else if ((uint)*(ushort *)(iVar2 + 0xc) <
                 (uint)*(ushort *)(puVar4 + 2) + (uint)*(ushort *)(puVar4 + 1)) {
          bVar1 = 0xd;
        }
        if (bVar1 != 0) {
          attsClearPrepWrites(param_1);
          break;
        }
      }
    }
    if (bVar1 == 0) {
      while (iVar2 = WsfQueueDeq(iVar3 + (uint)*(byte *)(param_1 + 0x24) * 8 + 0x238), iVar2 != 0) {
        bVar1 = attsExecPrepWrite(param_1,iVar2);
        if (bVar1 != 0) {
          attsClearPrepWrites(param_1);
        }
        WsfBufFree(iVar2);
      }
    }
  }
  else {
    bVar1 = 4;
  }
  if (bVar1 == 0) {
    iVar3 = attMsgAlloc(9);
    local_20 = param_2;
    if (iVar3 != 0) {
      *(undefined1 *)(iVar3 + 8) = 0x19;
      attL2cDataReq(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),1);
    }
  }
  else {
    local_20 = (uint)bVar1;
    attsErrRsp(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),0x18,0);
  }
  return CONCAT44(iStack_1c,local_20);
}

