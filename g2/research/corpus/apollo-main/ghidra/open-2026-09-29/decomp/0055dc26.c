
undefined8 FUN_0055dc26(uint *param_1)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = param_1[1];
  if ((param_1 == (uint *)0x0) || (uVar2 = DAT_0055e1f8, (*param_1 & 0x1ffffff) != DAT_0055e1f8)) {
    uVar1 = 2;
  }
  else if (*DAT_0055e1fc << 0x1f < 0) {
    uVar2 = *DAT_0055e204;
    *DAT_0055e204 = uVar2 | 0x80000000;
    uVar1 = 0;
    uVar2 = uVar2 | 0x80000000;
  }
  else {
    uVar1 = 7;
  }
  return CONCAT44(uVar2,uVar1);
}

