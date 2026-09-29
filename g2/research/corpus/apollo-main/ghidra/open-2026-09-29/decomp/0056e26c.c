
void attsProcReadGroupTypeReq(int param_1,char param_2,int param_3)

{
  ushort uVar1;
  ushort uVar2;
  char cVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  undefined1 *puVar10;
  undefined2 local_32;
  int local_30;
  int local_2c;
  undefined1 auStack_28 [4];
  
  iVar7 = 0;
  puVar10 = (undefined1 *)0x0;
  cVar3 = '\0';
  local_32 = *DAT_0056e4f4;
  uVar1 = *(ushort *)(*(int *)(param_1 + 0x10) + (uint)*(byte *)(param_1 + 0x25) * 4);
  uVar8 = (uint)*(byte *)(param_3 + 10) * 0x100 + (uint)*(byte *)(param_3 + 9);
  uVar2 = (ushort)*(byte *)(param_3 + 0xc) * 0x100 + (ushort)*(byte *)(param_3 + 0xb);
  local_2c = param_3 + 0xd;
  param_2 = param_2 + -5;
  if ((param_2 == '\x02') || (param_2 == '\x10')) {
    if ((uVar8 == 0) || (uVar2 < uVar8)) {
      cVar3 = '\x01';
    }
    else {
      iVar6 = attsUuid16Cmp(&local_32,param_2,local_2c);
      if (iVar6 == 0) {
        cVar3 = '\x10';
      }
    }
  }
  else {
    cVar3 = '\x04';
  }
  uVar4 = uVar8;
  if (cVar3 == '\0') {
    uVar4 = attsFindUuidInRange(uVar8,uVar2,param_2,local_2c,&local_30,auStack_28);
    if ((uVar4 & 0xffff) == 0) {
      cVar3 = '\n';
      uVar4 = uVar8;
    }
    else {
      cVar3 = attsPermissions(*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),1,uVar4 & 0xffff,
                              *(undefined1 *)(local_30 + 0xf));
      if (cVar3 == '\0') {
        iVar7 = attMsgAlloc(uVar1 + 8);
        if (iVar7 == 0) {
          cVar3 = '\x11';
          uVar4 = uVar8;
        }
        else {
          *(undefined1 *)(iVar7 + 8) = 0x11;
          if ((uint)**(ushort **)(local_30 + 8) < uVar1 - 6) {
            uVar9 = (uint)**(ushort **)(local_30 + 8);
          }
          else {
            uVar9 = uVar1 - 6;
          }
          *(char *)(iVar7 + 9) = (char)uVar9 + '\x04';
          *(char *)(iVar7 + 10) = (char)uVar4;
          *(char *)(iVar7 + 0xb) = (char)(uVar4 >> 8);
          uVar5 = attsFindServiceGroupEnd(uVar4 & 0xffff);
          *(char *)(iVar7 + 0xc) = (char)uVar5;
          *(char *)(iVar7 + 0xd) = (char)(uVar5 >> 8);
          FUN_00439be4(iVar7 + 0xe,*(undefined4 *)(local_30 + 4),uVar9 & 0xff);
          for (puVar10 = (undefined1 *)(iVar7 + 0xe + (uVar9 & 0xff));
              (((uVar4 = uVar8, (uVar5 & 0xffff) != 0xffff && ((uVar5 + 1 & 0xffff) <= (uint)uVar2))
               && (uVar5 = attsFindUuidInRange(uVar5 + 1 & 0xffff,uVar2,param_2,local_2c,&local_30,
                                               auStack_28), (uVar5 & 0xffff) != 0)) &&
              ((((uint)**(ushort **)(local_30 + 8) == (uVar9 & 0xff) &&
                (iVar6 = attsPermissions(*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),1,
                                         uVar5 & 0xffff,*(undefined1 *)(local_30 + 0xf)), iVar6 == 0
                )) && (puVar10 <= (undefined1 *)((((uint)uVar1 + iVar7) - (uVar9 & 0xff)) + 4)))));
              puVar10 = puVar10 + 4 + (uVar9 & 0xff)) {
            *puVar10 = (char)uVar5;
            puVar10[1] = (char)(uVar5 >> 8);
            uVar5 = attsFindServiceGroupEnd(uVar5 & 0xffff);
            puVar10[2] = (char)uVar5;
            puVar10[3] = (char)(uVar5 >> 8);
            FUN_00439be4(puVar10 + 4,*(undefined4 *)(local_30 + 4),uVar9 & 0xff);
          }
        }
      }
    }
  }
  attsDiscBusy(param_1);
  if (cVar3 == '\0') {
    attL2cDataReq(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),
                  (int)puVar10 - (iVar7 + 8) & 0xffff,iVar7);
  }
  else {
    attsErrRsp(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),0x10,uVar4 & 0xffff,
               cVar3);
  }
  return;
}

