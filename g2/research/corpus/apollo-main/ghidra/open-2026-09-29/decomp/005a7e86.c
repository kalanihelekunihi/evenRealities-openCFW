
undefined8
af_axis_hints_new_edge
          (int param_1,int param_2,char param_3,char param_4,undefined4 param_5,uint *param_6)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int local_20;
  
  local_20 = 0;
  uVar4 = 0;
  iVar7 = param_2;
  if (*(int *)(param_1 + 0xc) < 0xc) {
    if (*(int *)(param_1 + 0x14) == 0) {
      *(int *)(param_1 + 0x14) = param_1 + 0x334;
      *(undefined4 *)(param_1 + 0x10) = 0xc;
    }
  }
  else if (*(int *)(param_1 + 0x10) <= *(int *)(param_1 + 0xc)) {
    iVar3 = *(int *)(param_1 + 0x10);
    if (DAT_005a8a44 <= iVar3) {
      local_20 = 0x40;
      goto LAB_005a7f9a;
    }
    iVar5 = iVar3 + (iVar3 >> 2) + 4;
    if ((iVar5 < iVar3) || (DAT_005a8a44 < iVar5)) {
      iVar5 = DAT_005a8a44;
    }
    if (*(int *)(param_1 + 0x14) == param_1 + 0x334) {
      iVar7 = 0;
      uVar2 = ft_mem_realloc(param_5,0x2c,0,iVar5,0,&local_20);
      *(undefined4 *)(param_1 + 0x14) = uVar2;
      if (local_20 != 0) goto LAB_005a7f9a;
      FUN_00439be4(*(undefined4 *)(param_1 + 0x14),param_1 + 0x334,0x210);
    }
    else {
      iVar7 = *(int *)(param_1 + 0x14);
      uVar2 = ft_mem_realloc(param_5,0x2c,iVar3,iVar5,iVar7,&local_20);
      *(undefined4 *)(param_1 + 0x14) = uVar2;
      if (local_20 != 0) goto LAB_005a7f9a;
    }
    *(int *)(param_1 + 0x10) = iVar5;
  }
  uVar6 = *(uint *)(param_1 + 0x14);
  for (uVar4 = uVar6 + *(int *)(param_1 + 0xc) * 0x2c; uVar6 < uVar4; uVar4 = uVar4 - 0x2c) {
    if (param_4 == '\0') {
      if (*(short *)(uVar4 - 0x2c) < param_2) {
        bVar1 = true;
      }
      else {
        bVar1 = false;
      }
    }
    else if (param_2 < *(short *)(uVar4 - 0x2c)) {
      bVar1 = true;
    }
    else {
      bVar1 = false;
    }
    if ((bVar1) || ((*(short *)(uVar4 - 0x2c) == param_2 && (param_3 == *(char *)(param_1 + 0x18))))
       ) break;
    FUN_00439c04(uVar4,uVar4 - 0x2c,0x2c);
  }
  *(int *)(param_1 + 0xc) = *(int *)(param_1 + 0xc) + 1;
LAB_005a7f9a:
  *param_6 = uVar4;
  return CONCAT44(iVar7,local_20);
}

