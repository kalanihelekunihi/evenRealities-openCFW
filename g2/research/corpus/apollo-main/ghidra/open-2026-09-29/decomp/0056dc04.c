
void attsProcFindTypeReq(int param_1,short param_2,int param_3)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int unaff_r4;
  uint uVar5;
  uint uVar6;
  char cVar7;
  undefined1 *unaff_r10;
  int local_34;
  char *local_30;
  undefined1 auStack_2c [4];
  int local_28;
  
  cVar7 = '\0';
  uVar1 = *(ushort *)(*(int *)(param_1 + 0x10) + (uint)*(byte *)(param_1 + 0x25) * 4);
  uVar5 = (uint)*(byte *)(param_3 + 10) * 0x100 + (uint)*(byte *)(param_3 + 9);
  uVar6 = (uint)*(byte *)(param_3 + 0xc) * 0x100 + (uint)*(byte *)(param_3 + 0xb);
  local_30 = (char *)(param_3 + 0xd);
  local_28 = param_3 + 0xf;
  param_2 = param_2 + -7;
  if ((uVar5 == 0) || (uVar6 < uVar5)) {
    cVar7 = '\x01';
  }
  if (cVar7 == '\0') {
    unaff_r4 = attMsgAlloc(uVar1 + 8);
    if (unaff_r4 == 0) {
      cVar7 = '\x11';
    }
    else {
      *(undefined1 *)(unaff_r4 + 8) = 7;
      unaff_r10 = (undefined1 *)(unaff_r4 + 9);
      uVar2 = uVar5;
      while (uVar2 = attsFindUuidInRange(uVar2 & 0xffff,uVar6,2,local_30,&local_34,auStack_2c),
            (uVar2 & 0xffff) != 0) {
        if (((int)((uint)*(byte *)(local_34 + 0xf) << 0x1f) < 0) &&
           ((param_2 == 0 ||
            ((param_2 == **(short **)(local_34 + 8) &&
             (iVar3 = FUN_004751c8(local_28,*(undefined4 *)(local_34 + 4),param_2), iVar3 == 0))))))
        {
          uVar4 = uVar2;
          if ((*local_30 == '\0') && (local_30[1] == '(')) {
            uVar4 = attsFindServiceGroupEnd(uVar2 & 0xffff);
          }
          if ((undefined1 *)((uint)uVar1 + unaff_r4 + 4) < unaff_r10) break;
          *unaff_r10 = (char)uVar2;
          unaff_r10[1] = (char)(uVar2 >> 8);
          unaff_r10[2] = (char)uVar4;
          unaff_r10[3] = (char)(uVar4 >> 8);
          unaff_r10 = unaff_r10 + 4;
          uVar2 = uVar4;
        }
        if ((uVar6 <= (uVar2 & 0xffff)) || ((uVar2 & 0xffff) == 0xffff)) break;
        uVar2 = uVar2 + 1;
      }
      if (unaff_r10 == (undefined1 *)(unaff_r4 + 9)) {
        WsfMsgFree(unaff_r4);
        cVar7 = '\n';
      }
    }
  }
  attsDiscBusy(param_1);
  if (cVar7 == '\0') {
    attL2cDataReq(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),
                  (int)unaff_r10 - (unaff_r4 + 8) & 0xffff,unaff_r4);
  }
  else {
    attsErrRsp(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),6,uVar5,cVar7);
  }
  return;
}

