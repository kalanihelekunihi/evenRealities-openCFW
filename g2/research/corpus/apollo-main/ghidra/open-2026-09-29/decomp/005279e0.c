
undefined4 FT_Outline_Copy(short *param_1,short *param_2)

{
  byte bVar1;
  undefined4 uVar2;
  
  if ((param_1 == (short *)0x0) || (param_2 == (short *)0x0)) {
    uVar2 = 0x14;
  }
  else if ((param_1[1] == param_2[1]) && (*param_1 == *param_2)) {
    if (param_1 == param_2) {
      uVar2 = 0;
    }
    else {
      if (param_1[1] != 0) {
        FUN_00439be4(*(undefined4 *)(param_2 + 2),*(undefined4 *)(param_1 + 2),(int)param_1[1] << 3)
        ;
        FUN_00439be4(*(undefined4 *)(param_2 + 4),*(undefined4 *)(param_1 + 4),(int)param_1[1]);
      }
      if (*param_1 != 0) {
        FUN_00439be4(*(undefined4 *)(param_2 + 6),*(undefined4 *)(param_1 + 6),(int)*param_1 << 1);
      }
      bVar1 = *(byte *)(param_2 + 8);
      *(undefined4 *)(param_2 + 8) = *(undefined4 *)(param_1 + 8);
      *(uint *)(param_2 + 8) = *(uint *)(param_2 + 8) & 0xfffffffe;
      *(uint *)(param_2 + 8) = bVar1 & 1 | *(uint *)(param_2 + 8);
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 6;
  }
  return uVar2;
}

