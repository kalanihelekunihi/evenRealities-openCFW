
void attsProcReadMultiVarReq(int param_1,short param_2,int param_3)

{
  ushort uVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined1 *puVar6;
  int iVar7;
  byte *pbVar8;
  uint uVar9;
  short local_30;
  int local_28;
  
  iVar7 = 0;
  uVar5 = 0;
  cVar2 = '\0';
  uVar1 = *(ushort *)(*(int *)(param_1 + 0x10) + (uint)*(byte *)(param_1 + 0x25) * 4);
  pbVar8 = (byte *)(param_3 + 9);
  local_30 = param_2 + -1;
  iVar3 = attMsgAlloc(uVar1 + 8);
  if (iVar3 != 0) {
    puVar6 = (undefined1 *)(iVar3 + 9);
    do {
      do {
        if (local_30 == 0) goto LAB_0056cd42;
        iVar7 = (uint)pbVar8[1] * 0x100 + (uint)*pbVar8;
        pbVar8 = pbVar8 + 2;
        local_30 = local_30 + -2;
        iVar4 = attsFindByHandle(iVar7,&local_28);
        if (iVar4 == 0) {
          cVar2 = '\x01';
          goto LAB_0056cd42;
        }
        cVar2 = attsPermissions(*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),1,iVar7,
                                *(undefined1 *)(iVar4 + 0xf));
      } while (cVar2 != '\0');
      if (((int)((uint)*(byte *)(iVar4 + 0xe) << 0x1d) < 0) && (*(int *)(local_28 + 8) != 0)) {
        cVar2 = (**(code **)(local_28 + 8))
                          (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),iVar7,0x20,0,iVar4);
      }
      else if (((int)((uint)*(byte *)(iVar4 + 0xe) << 0x1a) < 0) &&
              (*(int *)(DAT_0056cd98 + 0x26c) != 0)) {
        cVar2 = (**(code **)(DAT_0056cd98 + 0x26c))
                          (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),5,iVar7,
                           *(undefined4 *)(iVar4 + 4));
      }
      if (cVar2 != '\0') break;
      if ((int)(uint)**(ushort **)(iVar4 + 8) < (int)(((uint)uVar1 - (uVar5 & 0xffff)) + -9)) {
        uVar9 = (uint)**(ushort **)(iVar4 + 8);
      }
      else {
        uVar9 = (uVar1 - uVar5) - 9;
      }
      *puVar6 = (char)uVar9;
      puVar6[1] = (char)(uVar9 >> 8);
      FUN_00439be4(puVar6 + 2,*(undefined4 *)(iVar4 + 4),uVar9 & 0xffff);
      puVar6 = puVar6 + 2 + (uVar9 & 0xffff);
      uVar5 = uVar9 + uVar5 + 2;
    } while ((uint)**(ushort **)(iVar4 + 8) <= (uVar9 & 0xffff));
LAB_0056cd42:
    if (cVar2 == '\0') {
      *(undefined1 *)(iVar3 + 8) = 0x21;
      attL2cDataReq(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),
                    uVar5 + 1 & 0xffff,iVar3);
    }
    else {
      AttMsgFree(iVar3,0x21);
    }
  }
  if (cVar2 != '\0') {
    attsErrRsp(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),0x20,iVar7,cVar2);
  }
  return;
}

