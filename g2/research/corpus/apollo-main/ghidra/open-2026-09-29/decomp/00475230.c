
undefined8 FUN_00475230(undefined4 param_1,undefined4 param_2,uint param_3)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_00475288;
  if ((*DAT_00475288 + 0x400000U < param_3) || (param_3 < 0x400000)) {
    iVar2 = 6;
  }
  else if (DAT_00475288[2] == 8) {
    iVar2 = 5;
  }
  else {
    param_3 = param_3 | 3;
    iVar2 = DAT_00475288[2];
    DAT_00475288[2] = iVar2 + 1;
    iVar2 = FUN_004d09d8(param_1,&stack0xfffffff8,piVar1[1] + iVar2 * 4,1);
    if (iVar2 == 0) {
      *DAT_0047528c = *DAT_0047528c | 1;
    }
  }
  return CONCAT44(param_3,iVar2);
}

