
undefined8 FUN_005cfeaa(undefined4 param_1,int param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  uStack_14 = param_4;
  do {
    if (param_2 < 1) goto LAB_005cfecc;
    iVar1 = FUN_005cfaf4(param_1,1,0);
    param_2 = param_2 + -1;
  } while (iVar1 != 0);
LAB_005cfec8:
  uVar2 = 0xa0;
LAB_005cfeca:
  return CONCAT44(local_18,uVar2);
  while ((uVar3 = FUN_005cfb62(iVar1,local_18), (uVar3 & 0xff) != (param_3 & 0xff) &&
         ((uVar3 & 0xff) != 0x14))) {
LAB_005cfecc:
    iVar1 = FUN_005cfaf4(param_1,1,&local_18);
    if (iVar1 == 0) goto LAB_005cfec8;
  }
  uVar2 = 0;
  goto LAB_005cfeca;
}

