
uint attsHandleValueIndNtf
               (byte param_1,uint param_2,byte param_3,uint param_4,uint param_5,undefined1 param_6,
               char param_7)

{
  bool bVar1;
  int iVar2;
  ushort *puVar3;
  undefined4 uVar4;
  ushort uVar5;
  byte bVar6;
  uint local_28;
  
  bVar1 = false;
  WsfTaskLock();
  iVar2 = attsCcbByConnId(param_1,param_3);
  if (iVar2 == 0) {
    uVar5 = 0;
    bVar6 = 0;
  }
  else {
    uVar5 = *(ushort *)(*(int *)(iVar2 + 0x10) + (uint)param_3 * 4);
    bVar6 = (byte)(((uint)*(byte *)(*(int *)(iVar2 + 0x10) + (uint)param_3 * 4 + 2) << 0x1d) >> 0x1f
                  );
  }
  WsfTaskUnlock();
  local_28 = param_4;
  if (uVar5 != 0) {
    if (bVar6 == 0) {
      iVar2 = attsCsfIsClientChangeAware(param_1,param_2 & 0xffff);
      if (iVar2 != 0) {
        if ((uint)uVar5 < (param_4 & 0xffff) + 3) {
          attsExecCallback(param_1,param_2 & 0xffff,0x77);
        }
        else {
          puVar3 = (ushort *)WsfMsgAlloc(0xc);
          if (puVar3 != (ushort *)0x0) {
            *puVar3 = (ushort)param_1;
            *(undefined1 *)(puVar3 + 1) = 0x21;
            *(byte *)(puVar3 + 4) = param_3;
            if (param_7 == '\0') {
              uVar4 = attMsgAlloc(param_4 + 0xb & 0xffff);
              *(undefined4 *)(puVar3 + 2) = uVar4;
            }
            else {
              *(uint *)(puVar3 + 2) = param_5 - 0xb;
            }
            if (*(int *)(puVar3 + 2) == 0) {
              WsfMsgFree(puVar3);
            }
            else {
              **(short **)(puVar3 + 2) = (short)param_4 + 3;
              *(short *)(*(int *)(puVar3 + 2) + 2) = (short)param_2;
              iVar2 = *(int *)(puVar3 + 2);
              *(undefined1 *)(iVar2 + 8) = param_6;
              *(char *)(iVar2 + 9) = (char)param_2;
              *(char *)(iVar2 + 10) = (char)(param_2 >> 8);
              if (param_7 == '\0') {
                local_28 = param_5;
                FUN_00439be4(iVar2 + 0xb,param_5,param_4 & 0xffff);
              }
              WsfMsgSend(*(undefined1 *)(DAT_00533eb0 + 0x60),puVar3);
              bVar1 = true;
            }
          }
        }
      }
    }
    else {
      attsExecCallback(param_1,param_2 & 0xffff,0x71);
    }
  }
  if ((!bVar1) && (param_7 != '\0')) {
    AttMsgFree(param_5,param_6);
  }
  return local_28;
}

