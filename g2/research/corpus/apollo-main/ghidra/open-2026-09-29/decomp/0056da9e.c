
undefined8 attsProcReadBlobReq(int param_1,uint param_2,int param_3,undefined4 param_4)

{
  ushort uVar1;
  byte bVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  uint local_30;
  int local_2c;
  undefined4 uStack_28;
  
  uVar1 = *(ushort *)(*(int *)(param_1 + 0x10) + (uint)*(byte *)(param_1 + 0x25) * 4);
  iVar5 = (uint)*(byte *)(param_3 + 10) * 0x100 + (uint)*(byte *)(param_3 + 9);
  uVar6 = (uint)*(byte *)(param_3 + 0xc) * 0x100 + (uint)*(byte *)(param_3 + 0xb);
  local_2c = param_3;
  uStack_28 = param_4;
  uVar3 = attsFindByHandle(iVar5,&local_2c);
  local_30 = param_2;
  if (uVar3 == 0) {
    bVar2 = 1;
  }
  else {
    bVar2 = attsPermissions(*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),1,iVar5,
                            *(undefined1 *)(uVar3 + 0xf));
    if (bVar2 == 0) {
      if (**(ushort **)(uVar3 + 8) < uVar6) {
        bVar2 = 7;
      }
      else {
        if (((int)((uint)*(byte *)(uVar3 + 0xe) << 0x1d) < 0) && (*(int *)(local_2c + 8) != 0)) {
          bVar2 = (**(code **)(local_2c + 8))
                            (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),iVar5,0xc,uVar6);
          local_30 = uVar3;
        }
        else if (((int)((uint)*(byte *)(uVar3 + 0xe) << 0x1a) < 0) &&
                (*(int *)(DAT_0056e4e4 + 0x26c) != 0)) {
          bVar2 = (**(code **)(DAT_0056e4e4 + 0x26c))
                            (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),5,iVar5,
                             *(undefined4 *)(uVar3 + 4));
        }
        if (bVar2 == 0) {
          if ((int)(**(ushort **)(uVar3 + 8) - uVar6) < (int)(uVar1 - 1)) {
            uVar7 = **(ushort **)(uVar3 + 8) - uVar6;
          }
          else {
            uVar7 = uVar1 - 1;
          }
          iVar4 = attMsgAlloc(uVar7 + 9 & 0xffff);
          if (iVar4 != 0) {
            *(undefined1 *)(iVar4 + 8) = 0xd;
            FUN_00439be4(iVar4 + 9,*(int *)(uVar3 + 4) + uVar6,uVar7 & 0xffff);
            attL2cDataReq(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),
                          uVar7 + 1 & 0xffff,iVar4);
          }
        }
      }
    }
  }
  if (bVar2 != 0) {
    local_30 = (uint)bVar2;
    attsErrRsp(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),0xc,iVar5);
  }
  return CONCAT44(local_2c,local_30);
}

