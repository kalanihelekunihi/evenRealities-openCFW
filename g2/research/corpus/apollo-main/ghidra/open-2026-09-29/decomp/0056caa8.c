
undefined8 attsProcReadReq(int param_1,undefined4 param_2,uint param_3,int param_4)

{
  ushort uVar1;
  byte bVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  short sVar6;
  uint local_28;
  int local_24;
  
  uVar1 = *(ushort *)(*(int *)(param_1 + 0x10) + (uint)*(byte *)(param_1 + 0x25) * 4);
  iVar5 = (uint)*(byte *)(param_3 + 10) * 0x100 + (uint)*(byte *)(param_3 + 9);
  local_24 = param_4;
  uVar3 = attsFindByHandle(iVar5,&local_24);
  local_28 = param_3;
  if (uVar3 == 0) {
    bVar2 = 1;
  }
  else {
    bVar2 = attsPermissions(*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),1,iVar5,
                            *(undefined1 *)(uVar3 + 0xf));
    if (bVar2 == 0) {
      if (((int)((uint)*(byte *)(uVar3 + 0xe) << 0x1d) < 0) && (*(int *)(local_24 + 8) != 0)) {
        bVar2 = (**(code **)(local_24 + 8))
                          (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),iVar5,10,0);
        local_28 = uVar3;
      }
      else if (((int)((uint)*(byte *)(uVar3 + 0xe) << 0x1a) < 0) &&
              (*(int *)(DAT_0056cd98 + 0x26c) != 0)) {
        bVar2 = (**(code **)(DAT_0056cd98 + 0x26c))
                          (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),5,iVar5,
                           *(undefined4 *)(uVar3 + 4));
      }
      if (bVar2 == 0) {
        if ((int)(uint)**(ushort **)(uVar3 + 8) < (int)(uVar1 - 1)) {
          sVar6 = **(short **)(uVar3 + 8);
        }
        else {
          sVar6 = uVar1 - 1;
        }
        iVar4 = attMsgAlloc(sVar6 + 9);
        if (iVar4 != 0) {
          *(undefined1 *)(iVar4 + 8) = 0xb;
          FUN_00439be4(iVar4 + 9,*(undefined4 *)(uVar3 + 4),sVar6);
          attL2cDataReq(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),sVar6 + 1,
                        iVar4);
        }
      }
    }
  }
  if (bVar2 != 0) {
    local_28 = (uint)bVar2;
    attsErrRsp(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),10,iVar5);
  }
  return CONCAT44(local_24,local_28);
}

