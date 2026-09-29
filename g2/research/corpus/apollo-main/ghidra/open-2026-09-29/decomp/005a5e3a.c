
undefined8 attsProcWrite(uint param_1,int param_2,int param_3,int param_4)

{
  char cVar1;
  byte bVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  int local_24;
  
  cVar1 = *(char *)(param_3 + 8);
  iVar5 = (uint)*(byte *)(param_3 + 10) * 0x100 + (uint)*(byte *)(param_3 + 9);
  iVar4 = param_3 + 0xb;
  uVar6 = param_2 - 3;
  uVar7 = param_1;
  local_24 = param_4;
  iVar3 = attsFindByHandle(iVar5,&local_24);
  if (iVar3 == 0) {
    bVar2 = 1;
  }
  else {
    bVar2 = attsPermissions(*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),0x10,iVar5,
                            *(undefined1 *)(iVar3 + 0xf),uVar7,param_2,param_3);
    if (bVar2 == 0) {
      if (((int)((uint)*(byte *)(iVar3 + 0xe) << 0x1c) < 0) ||
         ((uVar6 & 0xffff) == (uint)*(ushort *)(iVar3 + 0xc))) {
        if (((int)((uint)*(byte *)(iVar3 + 0xe) << 0x1c) < 0) &&
           ((uint)*(ushort *)(iVar3 + 0xc) < (uVar6 & 0xffff))) {
          bVar2 = 0xd;
        }
        else {
          if (((int)((uint)*(byte *)(iVar3 + 0xe) << 0x1e) < 0) && (*(int *)(local_24 + 0xc) != 0))
          {
            uVar7 = uVar6 & 0xffff;
            bVar2 = (**(code **)(local_24 + 0xc))
                              (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),iVar5,cVar1,0,uVar7,
                               iVar4,iVar3);
            param_2 = iVar4;
          }
          else if (((int)((uint)*(byte *)(iVar3 + 0xe) << 0x1a) < 0) &&
                  (*(int *)(DAT_005a6258 + 0x26c) != 0)) {
            bVar2 = (**(code **)(DAT_005a6258 + 0x26c))
                              (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),9,iVar5,iVar4);
          }
          else {
            FUN_00439be4(*(undefined4 *)(iVar3 + 4),iVar4,uVar6 & 0xffff);
            if ((int)((uint)*(byte *)(iVar3 + 0xe) << 0x1c) < 0) {
              **(undefined2 **)(iVar3 + 8) = (short)uVar6;
            }
          }
          if (((bVar2 == 0) && (cVar1 == '\x12')) && (iVar3 = attMsgAlloc(9), iVar3 != 0)) {
            *(undefined1 *)(iVar3 + 8) = 0x13;
            attL2cDataReq(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),1);
          }
        }
      }
      else {
        bVar2 = 0xd;
      }
    }
  }
  if ((bVar2 != 0) && (cVar1 == '\x12')) {
    if (bVar2 == 0x7a) {
      *(byte *)(*(int *)(param_1 + 0x10) + (uint)*(byte *)(param_1 + 0x25) * 4 + 2) =
           *(byte *)(*(int *)(param_1 + 0x10) + (uint)*(byte *)(param_1 + 0x25) * 4 + 2) | 8;
    }
    else {
      uVar7 = (uint)bVar2;
      attsErrRsp(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),0x12,iVar5);
    }
  }
  return CONCAT44(param_2,uVar7);
}

