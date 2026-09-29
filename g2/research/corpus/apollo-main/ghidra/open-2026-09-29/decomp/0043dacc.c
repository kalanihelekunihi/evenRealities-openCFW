
void FUN_0043dacc(undefined4 param_1,uint param_2,int param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  undefined1 uVar6;
  uint uVar7;
  ushort uVar8;
  undefined1 auStack_30 [8];
  undefined4 local_28;
  
  FUN_0043c0e4(auStack_30,8,0);
  if (((DAT_0043dcb4[0xf1] != 0) && (3 < *DAT_0043dcb4)) &&
     (local_28 = param_1, iVar1 = FUN_0044b63a(param_1,DAT_0043dcb4 + 1), iVar1 != 0)) {
    FUN_0043d416();
    for (uVar7 = 0; iVar1 = DAT_0043dc8c, (uVar7 & 0xffff) < (param_4 & 0xffff);
        uVar7 = uVar7 + (param_2 & 0xff)) {
      iVar2 = (param_2 & 0xff) + (uVar7 & 0xffff) + -1;
      uVar3 = uVar7 & 0xffff;
      uVar4 = FUN_0044b728(DAT_0043dc8c,0x400,DAT_0043dcb8,local_28,uVar3,iVar2);
      if (0x400 < uVar4) {
        uVar4 = 0x400;
      }
      for (uVar8 = 0; (uint)uVar8 < (param_2 & 0xff); uVar8 = uVar8 + 1) {
        if ((uint)uVar8 + (uVar7 & 0xffff) < (param_4 & 0xffff)) {
          FUN_0044b728(auStack_30,8,DAT_0043dcbc,
                       *(undefined1 *)(param_3 + (uint)uVar8 + (uVar7 & 0xffff)),uVar3,iVar2);
        }
        else {
          FUN_0044b5a0(auStack_30,&DAT_0043dc90,8);
        }
        iVar5 = elog_strcpy(uVar4 & 0xffff,iVar1 + (uVar4 & 0xffff),auStack_30);
        uVar4 = iVar5 + uVar4;
        if ((uVar8 + 1 & 7) == 0) {
          iVar5 = elog_strcpy(uVar4 & 0xffff,iVar1 + (uVar4 & 0xffff),&DAT_0043dc98);
          uVar4 = iVar5 + uVar4;
        }
      }
      iVar5 = elog_strcpy(uVar4 & 0xffff,iVar1 + (uVar4 & 0xffff),&DAT_0043dc9c);
      uVar4 = iVar5 + uVar4;
      for (uVar8 = 0; (uint)uVar8 < (param_2 & 0xff); uVar8 = uVar8 + 1) {
        if ((uint)uVar8 + (uVar7 & 0xffff) < (param_4 & 0xffff)) {
          if (*(byte *)(param_3 + (uint)uVar8 + (uVar7 & 0xffff)) - 0x20 < 0x5f) {
            uVar6 = *(undefined1 *)(param_3 + (uint)uVar8 + (uVar7 & 0xffff));
          }
          else {
            uVar6 = 0x2e;
          }
          FUN_0044b728(auStack_30,8,&DAT_0043dca0,uVar6,uVar3,iVar2);
          iVar5 = elog_strcpy(uVar4 & 0xffff,iVar1 + (uVar4 & 0xffff),auStack_30);
          uVar4 = iVar5 + uVar4;
        }
      }
      if (0x400 < (uVar4 & 0xffff) + 1) {
        uVar4 = 0x3ff;
      }
      iVar2 = elog_strcpy(uVar4 & 0xffff,iVar1 + (uVar4 & 0xffff),&DAT_0043dc88);
      FUN_0044aa76(iVar1,iVar2 + uVar4 & 0xffff);
    }
    FUN_0043d438();
  }
  return;
}

