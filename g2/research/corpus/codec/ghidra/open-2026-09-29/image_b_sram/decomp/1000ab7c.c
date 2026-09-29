
undefined4 FUN_1000ab7c(uint param_1,int param_2,uint *param_3)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  
  iVar7 = DAT_1000acac;
  iVar8 = param_1 * 4;
  iVar3 = DAT_1000acac + iVar8;
  iVar2 = *(int *)(iVar3 + 0x2f8);
  if (iVar2 == 0) {
    iVar5 = *(int *)(param_2 + 0x18);
    *(int *)(iVar3 + 0x300) = iVar5;
    if (iVar5 == 0) goto LAB_1000ac44;
  }
  else {
    iVar5 = *(int *)(iVar3 + 0x300);
    if (iVar5 == iVar2) {
LAB_1000ac44:
      *(undefined4 *)(iVar7 + iVar8 + 0x2f8) = 0;
      iVar7 = DAT_1000acac;
      if (((param_1 & 0xff) != 0) && (iVar7 = DAT_1000acb8, (param_1 & 0xff) != 1)) {
        return 0xffffffff;
      }
      *(uint *)(iVar7 + 0x174) = (byte)~(*(char *)(iVar7 + 0x43) != '\0') + 2;
      FUN_10004650(param_1,PTR_LAB_1000acb4,0);
      return 1;
    }
  }
  if (((param_2 != 0) && (param_3 != (uint *)0x0)) && (uVar6 = *param_3, uVar6 != 0)) {
    bVar1 = (uint)(iVar5 - iVar2) < uVar6;
    iVar3 = bVar1 * uVar6 + !bVar1 * uVar6;
    FUN_10004614(param_1,iVar2 + *(int *)(param_2 + 0x10),iVar3);
    iVar2 = iVar7 + iVar8;
    uVar4 = *(int *)(iVar2 + 0x2f8) + iVar3;
    uVar6 = *(uint *)(iVar2 + 0x300);
    if (uVar4 == uVar6) {
      *(undefined4 *)(iVar2 + 0x2f8) = 0;
      *param_3 = *param_3 - iVar3;
    }
    else {
      *(uint *)(iVar2 + 0x2f8) = uVar4;
      *param_3 = *param_3 - iVar3;
      if (uVar4 != 0) {
        if ((*(int *)(param_2 + 0x10) + uVar4 & 0xf) == 0) {
          uVar6 = uVar6 - uVar4;
        }
        else if ((uVar4 < 0x10) || (uVar6 = uVar6 - uVar4, uVar6 < 0x21)) {
          return 0;
        }
        iVar7 = iVar7 + iVar8;
        FUN_10004684(param_1);
        FUN_10004740(param_1,*(int *)(iVar7 + 0x2f8) + *(int *)(param_2 + 0x10),uVar6 & 0xfffffff0,
                     PTR_LAB_1000acb0,0);
        *(uint *)(iVar7 + 0x2f8) = *(int *)(iVar7 + 0x2f8) + (uVar6 & 0xfffffff0);
        *param_3 = 0;
        return 0;
      }
    }
    return 1;
  }
  FUN_10004650(param_1,PTR_LAB_1000acb4,0);
  return 0xffffffff;
}

