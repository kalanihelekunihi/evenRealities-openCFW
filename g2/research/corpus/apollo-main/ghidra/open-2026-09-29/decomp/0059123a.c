
int FUN_0059123a(undefined4 param_1,int param_2,int param_3,int param_4,int param_5)

{
  longlong lVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  bool bVar8;
  undefined1 local_4d8;
  undefined1 local_4d7;
  undefined1 local_4d6;
  int local_38;
  int local_34;
  int local_30;
  
  if (param_4 < 1) {
    param_4 = param_3;
  }
  iVar2 = FUN_00590d3c(param_2,param_1);
  uVar3 = FUN_00590d74(param_3,param_1);
  uVar4 = FUN_00590d74(param_4,param_1);
  bVar8 = SBORROW4(iVar2,4);
  iVar7 = iVar2 + -4;
  if (iVar2 < 4) {
    bVar8 = SBORROW4(uVar4,7);
    iVar7 = uVar4 - 7;
  }
  if (((iVar7 < 0 != bVar8) && (uVar3 <= uVar4)) && (param_5 != 0)) {
    iVar7 = *(int *)(DAT_005915a8 + uVar4 * 4);
    iVar6 = (iVar2 + 1) * iVar7;
    iVar7 = iVar7 >> 1;
    FUN_0048949c(&local_4d8,0x4b0);
    local_4d8 = (undefined1)iVar2;
    local_4d7 = (undefined1)uVar3;
    local_34 = (iVar7 + iVar6) / 2;
    local_30 = iVar6 + local_34;
    local_4d6 = (undefined1)uVar4;
    local_38 = iVar7;
    FUN_00439c04(param_5,&local_4d8,0x4b0);
    if (param_2 == 0x1d4c) {
      iVar7 = 2000;
    }
    else {
      iVar7 = 0x4e2;
    }
    iVar2 = (int)((ulonglong)((longlong)(param_4 * param_2) * (longlong)DAT_005915c8) >> 0x20);
    iVar6 = (int)((ulonglong)((longlong)(param_4 * 0x4e2) * (longlong)DAT_005915c8) >> 0x20);
    iVar2 = (int)((ulonglong)((longlong)((iVar2 >> 6) - (iVar2 >> 0x1f)) * (longlong)DAT_005915c8)
                 >> 0x20);
    iVar5 = (int)((ulonglong)((longlong)((iVar6 >> 6) - (iVar6 >> 0x1f)) * (longlong)DAT_005915c8)
                 >> 0x20);
    iVar2 = (iVar2 >> 6) - (iVar2 >> 0x1f);
    lVar1 = (longlong)(iVar7 * param_4) * (longlong)DAT_005915c8;
    iVar7 = (int)((ulonglong)lVar1 >> 0x20);
    iVar6 = (iVar7 >> 6) - (iVar7 >> 0x1f);
    iVar7 = (int)((ulonglong)((longlong)iVar6 * (longlong)DAT_005915c8) >> 0x20);
    FUN_004d4ccc(param_5 + 0x4ac,
                 (((iVar7 >> 6) - (iVar7 >> 0x1f)) +
                 iVar2 + (((iVar5 >> 6) - (iVar5 >> 0x1f)) + iVar2) / 2 + iVar2 / 2) * 4,iVar6,
                 (int)lVar1);
    return param_5;
  }
  return 0;
}

