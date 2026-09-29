
void attsProcReadTypeReq(int param_1,char param_2,int param_3)

{
  ushort uVar1;
  char cVar2;
  char cVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  undefined1 *puVar9;
  byte local_38;
  int local_34;
  ushort local_30;
  int local_2c;
  int local_28;
  
  iVar7 = 0;
  puVar9 = (undefined1 *)0x0;
  cVar3 = '\0';
  cVar2 = '\0';
  uVar1 = *(ushort *)(*(int *)(param_1 + 0x10) + (uint)*(byte *)(param_1 + 0x25) * 4);
  uVar8 = (uint)*(byte *)(param_3 + 10) * 0x100 + (uint)*(byte *)(param_3 + 9);
  local_30 = (ushort)*(byte *)(param_3 + 0xc) * 0x100 + (ushort)*(byte *)(param_3 + 0xb);
  local_28 = param_3 + 0xd;
  param_2 = param_2 + -5;
  if ((param_2 == '\x02') || (param_2 == '\x10')) {
    if ((uVar8 == 0) || (local_30 < uVar8)) {
      cVar2 = '\x01';
    }
  }
  else {
    cVar2 = '\x04';
  }
  if (cVar2 == '\0') {
    uVar8 = attsFindUuidInRange(uVar8,local_30,param_2,local_28,&local_34,&local_2c);
    if ((uVar8 & 0xffff) == 0) {
      cVar2 = '\n';
    }
    else {
      cVar2 = attsPermissions(*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),1,uVar8 & 0xffff,
                              *(undefined1 *)(local_34 + 0xf));
      if (cVar2 == '\0') {
        if (((int)((uint)*(byte *)(local_34 + 0xe) << 0x1d) < 0) && (*(int *)(local_2c + 8) != 0)) {
          cVar2 = (**(code **)(local_2c + 8))
                            (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),uVar8 & 0xffff,8,0,
                             local_34);
        }
        else if (((int)((uint)*(byte *)(local_34 + 0xe) << 0x1a) < 0) &&
                (*(int *)(DAT_0056e4e4 + 0x26c) != 0)) {
          cVar2 = (**(code **)(DAT_0056e4e4 + 0x26c))
                            (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),5,uVar8 & 0xffff,
                             *(undefined4 *)(local_34 + 4));
        }
      }
    }
    if (cVar2 == '\0') {
      iVar7 = FUN_004751c8(local_28,DAT_0056e4f0,2);
      if ((iVar7 == 0) && (iVar7 = attsCsfGetHashUpdateStatus(), iVar7 != 0)) {
        uVar4 = WsfBufAlloc(4);
        *(undefined4 *)(*(int *)(param_1 + 0x10) + 0x10) = uVar4;
        if (*(int *)(*(int *)(param_1 + 0x10) + 0x10) != 0) {
          **(undefined2 **)(*(int *)(param_1 + 0x10) + 0x10) = (short)uVar8;
          *(short *)(*(int *)(*(int *)(param_1 + 0x10) + 0x10) + 2) = (short)uVar8;
          return;
        }
        attsErrRsp(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),8,uVar8 & 0xffff,
                   0x11);
        return;
      }
      iVar7 = attMsgAlloc(uVar1 + 8);
      if (iVar7 == 0) {
        cVar2 = '\x11';
      }
      else {
        *(undefined1 *)(iVar7 + 8) = 9;
        if ((uint)**(ushort **)(local_34 + 8) < uVar1 - 4) {
          local_38 = (byte)**(undefined2 **)(local_34 + 8);
        }
        else {
          local_38 = (char)uVar1 - 4;
        }
        *(byte *)(iVar7 + 9) = local_38 + 2;
        *(char *)(iVar7 + 10) = (char)uVar8;
        *(char *)(iVar7 + 0xb) = (char)(uVar8 >> 8);
        FUN_00439be4(iVar7 + 0xc,*(undefined4 *)(local_34 + 4),local_38);
        puVar9 = (undefined1 *)(iVar7 + 0xc + (uint)local_38);
        uVar6 = uVar8 + 1;
        while (uVar6 = attsFindUuidInRange(uVar6 & 0xffff,local_30,param_2,local_28,&local_34,
                                           &local_2c), (uVar6 & 0xffff) != 0) {
          if (((int)((uint)*(byte *)(local_34 + 0xe) << 0x1d) < 0) && (*(int *)(local_2c + 8) != 0))
          {
            cVar3 = (**(code **)(local_2c + 8))
                              (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),uVar6 & 0xffff,8,0,
                               local_34);
          }
          else if (((int)((uint)*(byte *)(local_34 + 0xe) << 0x1a) < 0) &&
                  (*(int *)(DAT_0056e4e4 + 0x26c) != 0)) {
            cVar3 = (**(code **)(DAT_0056e4e4 + 0x26c))
                              (*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),5,uVar6 & 0xffff,
                               *(undefined4 *)(local_34 + 4));
          }
          if ((((cVar3 != '\0') || (**(ushort **)(local_34 + 8) != (ushort)local_38)) ||
              (iVar5 = attsPermissions(*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),1,
                                       uVar6 & 0xffff,*(undefined1 *)(local_34 + 0xf)), iVar5 != 0))
             || ((undefined1 *)((((uint)uVar1 + iVar7) - (uint)local_38) + 6) < puVar9)) break;
          *puVar9 = (char)uVar6;
          puVar9[1] = (char)(uVar6 >> 8);
          FUN_00439be4(puVar9 + 2,*(undefined4 *)(local_34 + 4),local_38);
          puVar9 = puVar9 + 2 + local_38;
          if (((uVar6 & 0xffff) == 0xffff) || (uVar6 = uVar6 + 1, (uint)local_30 < (uVar6 & 0xffff))
             ) break;
        }
      }
    }
  }
  if (cVar2 == '\0') {
    attL2cDataReq(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),
                  (int)puVar9 - (iVar7 + 8) & 0xffff,iVar7);
  }
  else {
    attsErrRsp(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),8,uVar8 & 0xffff,
               cVar2);
  }
  return;
}

