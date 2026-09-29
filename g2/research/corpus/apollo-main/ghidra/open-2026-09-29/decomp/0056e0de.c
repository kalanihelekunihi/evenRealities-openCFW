
void attsProcReadMultReq(int param_1,ushort param_2,int param_3,undefined4 param_4)

{
  ushort uVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  uint unaff_r6;
  int iVar5;
  byte *pbVar6;
  uint uVar7;
  int local_30;
  byte *local_2c;
  undefined4 uStack_28;
  
  iVar5 = 0;
  cVar2 = '\0';
  uVar1 = *(ushort *)(*(int *)(param_1 + 0x10) + (uint)*(byte *)(param_1 + 0x25) * 4);
  local_2c = (byte *)(param_3 + (uint)param_2 + 8);
  pbVar6 = (byte *)(param_3 + 9);
  uStack_28 = param_4;
  iVar3 = attMsgAlloc(uVar1 + 8);
  if (iVar3 == 0) {
    cVar2 = '\x11';
  }
  else {
    *(undefined1 *)(iVar3 + 8) = 0xf;
    unaff_r6 = iVar3 + 9;
    while (pbVar6 < local_2c) {
      iVar5 = (uint)pbVar6[1] * 0x100 + (uint)*pbVar6;
      pbVar6 = pbVar6 + 2;
      iVar4 = attsFindByHandle(iVar5,&local_30);
      if (iVar4 == 0) {
        cVar2 = '\x01';
        break;
      }
      cVar2 = attsPermissions(*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),1,iVar5,
                              *(undefined1 *)(iVar4 + 0xf));
      if (cVar2 != '\0') break;
      if (((int)((uint)*(byte *)(iVar4 + 0xe) << 0x1d) < 0) && (*(int *)(local_30 + 8) != 0)) {
        cVar2 = (**(code **)(local_30 + 8))
                          (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),iVar5,0xe,0,iVar4);
joined_r0x0056e1ec:
        if (cVar2 != '\0') break;
      }
      else if (((int)((uint)*(byte *)(iVar4 + 0xe) << 0x1a) < 0) &&
              (*(int *)(DAT_0056e4e4 + 0x26c) != 0)) {
        cVar2 = (**(code **)(DAT_0056e4e4 + 0x26c))
                          (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),5,iVar5,
                           *(undefined4 *)(iVar4 + 4));
        goto joined_r0x0056e1ec;
      }
      if (unaff_r6 < (uint)uVar1 + iVar3 + 8) {
        uVar7 = ((uint)uVar1 + iVar3 + 8) - unaff_r6;
        if ((uint)**(ushort **)(iVar4 + 8) < (uVar7 & 0xffff)) {
          uVar7 = (uint)**(ushort **)(iVar4 + 8);
        }
        FUN_00439be4(unaff_r6,*(undefined4 *)(iVar4 + 4),uVar7 & 0xffff);
        unaff_r6 = unaff_r6 + (uVar7 & 0xffff);
      }
    }
  }
  if (cVar2 == '\0') {
    attL2cDataReq(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),
                  unaff_r6 - (iVar3 + 8) & 0xffff,iVar3);
  }
  else {
    if (iVar3 != 0) {
      WsfMsgFree(iVar3);
    }
    attsErrRsp(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),0xe,iVar5,cVar2);
  }
  return;
}

