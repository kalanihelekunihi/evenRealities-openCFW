
void attsProcPrepWriteReq(int param_1,short param_2,int param_3,undefined4 param_4)

{
  char cVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  short sVar7;
  int local_2c;
  undefined4 uStack_28;
  
  iVar4 = 0;
  iVar5 = (uint)*(byte *)(param_3 + 10) * 0x100 + (uint)*(byte *)(param_3 + 9);
  iVar6 = (uint)*(byte *)(param_3 + 0xc) * 0x100 + (uint)*(byte *)(param_3 + 0xb);
  param_3 = param_3 + 0xd;
  sVar7 = param_2 + -5;
  uStack_28 = param_4;
  iVar3 = attsFindByHandle(iVar5,&local_2c);
  if (iVar3 == 0) {
    cVar1 = '\x01';
  }
  else {
    cVar1 = attsPermissions(*(undefined1 *)(param_1 + 0x24),0x10,iVar5,*(undefined1 *)(iVar3 + 0xf))
    ;
    if (cVar1 == '\0') {
      if ((iVar6 == 0) || ((int)((uint)*(byte *)(iVar3 + 0xe) << 0x1b) < 0)) {
        if (((int)((uint)*(byte *)(iVar3 + 0xe) << 0x1c) < 0) || (sVar7 == *(short *)(iVar3 + 0xc)))
        {
          uVar2 = WsfQueueCount(DAT_005a6258 + (uint)*(byte *)(param_1 + 0x24) * 8 + 0x238);
          if (uVar2 < *(byte *)(*DAT_005a625c + 7)) {
            iVar4 = WsfBufAlloc(param_2 + 6);
            if (iVar4 == 0) {
              cVar1 = '\x11';
            }
            else if (((int)((uint)*(byte *)(iVar3 + 0xe) << 0x1e) < 0) &&
                    (*(int *)(local_2c + 0xc) != 0)) {
              cVar1 = (**(code **)(local_2c + 0xc))
                                (*(undefined1 *)(param_1 + 0x24),iVar5,0x16,0,sVar7,param_3,iVar3);
            }
          }
          else {
            cVar1 = '\t';
          }
        }
        else {
          cVar1 = '\r';
        }
      }
      else {
        cVar1 = '\v';
      }
    }
  }
  if (cVar1 == '\0') {
    *(short *)(iVar4 + 4) = sVar7;
    *(short *)(iVar4 + 6) = (short)iVar5;
    *(short *)(iVar4 + 8) = (short)iVar6;
    FUN_00439be4(iVar4 + 10,param_3,sVar7);
    WsfQueueEnq(DAT_005a6258 + (uint)*(byte *)(param_1 + 0x24) * 8 + 0x238,iVar4);
    iVar3 = attMsgAlloc(param_2 + 8);
    if (iVar3 != 0) {
      *(undefined1 *)(iVar3 + 8) = 0x17;
      *(char *)(iVar3 + 9) = (char)iVar5;
      *(char *)(iVar3 + 10) = (char)((uint)iVar5 >> 8);
      *(char *)(iVar3 + 0xb) = (char)iVar6;
      *(char *)(iVar3 + 0xc) = (char)((uint)iVar6 >> 8);
      FUN_00439be4(iVar3 + 0xd,param_3,sVar7);
      attL2cDataReq(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),param_2,iVar3);
    }
  }
  if (cVar1 != '\0') {
    attsErrRsp(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),0x16,iVar5,cVar1);
  }
  return;
}

