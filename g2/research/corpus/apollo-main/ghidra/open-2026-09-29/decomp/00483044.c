
undefined8
FUN_00483044(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte *pbVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  while (iVar2 = FUN_00483032(*(undefined1 *)*param_1), iVar2 != 0) {
    pbVar1 = (byte *)*param_1;
    *param_1 = pbVar1 + 1;
    iVar3 = iVar3 * 10 + (*pbVar1 - 0x30);
  }
  return CONCAT44(param_4,iVar3);
}

