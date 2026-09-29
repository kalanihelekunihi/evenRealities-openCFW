
undefined8 FUN_0055dae4(uint *param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055e1f8)) {
    iVar1 = 2;
  }
  else if (*param_2 == 2) {
    iVar1 = FUN_004c44bc(4,0xf);
    if (iVar1 == 0) {
      *DAT_0055e1fc =
           (*param_2 & 7) << 0x18 | (param_2[1] & 1) << 0x14 | (param_2[2] & 1) << 0x13 |
           (param_2[3] & 7) << 0x10 | 0x1000 | (param_2[4] & 1) << 4 | (param_2[5] & 1) << 3 |
           (param_2[6] & 1) << 2;
      iVar1 = 0;
    }
  }
  else {
    iVar1 = 6;
  }
  return CONCAT44(param_4,iVar1);
}

