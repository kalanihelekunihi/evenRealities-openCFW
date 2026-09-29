
undefined8 FUN_005d8c3e(uint *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  byte *pbVar2;
  
  iVar1 = 0;
  if (*param_1 <= param_2) {
    iVar1 = FUN_005d8bc0(param_1,param_2 + 1);
    if (iVar1 != 0) goto LAB_005d8c74;
    *param_1 = param_2 + 1;
  }
  pbVar2 = (byte *)(param_1[2] + (param_2 >> 3));
  *pbVar2 = *pbVar2 | 0x80U >> (param_2 & 7);
LAB_005d8c74:
  return CONCAT44(param_4,iVar1);
}

