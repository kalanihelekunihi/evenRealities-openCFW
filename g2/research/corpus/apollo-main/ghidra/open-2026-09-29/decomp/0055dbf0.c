
undefined4 FUN_0055dbf0(uint *param_1,int param_2)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055e1f8)) {
    uVar1 = 2;
  }
  else {
    *DAT_0055e204 = (*(byte *)(param_2 + 1) & 7) << 0x10 | *(uint *)(param_2 + 4) & 0x3ff;
    uVar1 = 0;
  }
  return uVar1;
}

