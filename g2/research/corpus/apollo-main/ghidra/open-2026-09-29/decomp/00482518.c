
undefined8 FUN_00482518(int *param_1,int param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  int iVar2;
  char cVar3;
  int extraout_r2;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  bool bVar8;
  longlong lVar9;
  undefined4 local_28;
  int local_24;
  
  iVar4 = param_1[4];
  if (param_2 == 0x6f) {
    iVar5 = 8;
  }
  else {
    iVar5 = FUN_00481830();
    if (iVar5 == 0x78) {
      iVar5 = 0x10;
    }
    else {
      iVar5 = 10;
    }
  }
  iVar1 = *param_1;
  iVar2 = param_1[1];
  iVar6 = 0x3c;
  if ((param_2 == 100 || param_2 == 0x69) && (iVar2 < 0)) {
    bVar8 = iVar1 != 0;
    iVar1 = -iVar1;
    iVar2 = -iVar2 - (uint)bVar8;
  }
  lVar9 = CONCAT44(iVar2,iVar1);
  if ((iVar2 == 0 && iVar1 == 0) && (param_1[0xc] == 0)) {
    local_28 = param_3;
    local_24 = param_4;
    if ((iVar5 == 8) && ((int)((uint)*(byte *)(param_1 + 0xe) << 0x1c) < 0)) {
      *(undefined1 *)(iVar4 + 0x3b) = 0x30;
      iVar6 = 0x3b;
    }
  }
  else {
    local_28 = CONCAT31((int3)((uint)param_3 >> 8),(char)param_2);
    do {
      iVar1 = iVar6;
      uVar7 = (undefined4)((ulonglong)lVar9 >> 0x20);
      FUN_0047cc60((int)lVar9,uVar7,iVar5,0);
      cVar3 = (char)(extraout_r2 + 0x30U);
      local_24 = iVar1 + -1;
      if (0x39 < (extraout_r2 + 0x30U & 0xff)) {
        cVar3 = cVar3 + (char)param_2 + -0x51;
      }
      *(char *)(iVar4 + local_24) = cVar3;
      lVar9 = FUN_0047cc60((int)lVar9,uVar7,iVar5,0);
      iVar6 = local_24;
    } while ((lVar9 != 0) && ((uint)param_1[3] < (uint)(iVar4 + local_24)));
    if ((iVar5 == 8) &&
       (((int)((uint)*(byte *)(param_1 + 0xe) << 0x1c) < 0 && (*(char *)(iVar4 + local_24) != '0')))
       ) {
      iVar6 = iVar1 + -2;
      *(undefined1 *)(iVar4 + iVar6) = 0x30;
    }
  }
  iVar5 = 0x3c - iVar6;
  param_1[6] = iVar5;
  param_1[3] = iVar4 + iVar6;
  iVar4 = param_1[0xc];
  if (iVar4 <= iVar5) {
    if ((iVar4 < 0) && ((*(byte *)(param_1 + 0xe) & 0x14) == 0x10)) {
      iVar5 = ((param_1[0xd] - param_1[5]) - param_1[8]) - iVar5;
      if (0 < iVar5) {
        param_1[8] = iVar5;
      }
    }
    return CONCAT44(local_24,local_28);
  }
  param_1[8] = iVar4 - iVar5;
  *(ushort *)(param_1 + 0xe) = *(ushort *)(param_1 + 0xe) & 0xffef;
  return CONCAT44(local_24,local_28);
}

