
undefined4 FUN_0055de1c(uint *param_1)

{
  uint *puVar1;
  undefined4 uVar2;
  
  puVar1 = DAT_0055e1fc;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055e1f8)) {
    uVar2 = 2;
  }
  else {
    *DAT_0055e1fc = *DAT_0055e1fc & 0xfffffffb;
    *puVar1 = *puVar1 & 0xfffffffe;
    if ((*puVar1 & 0x7ffffff) >> 0x18 == 3) {
      *puVar1 = *puVar1 & 0xf8ffffff;
    }
    FUN_004c4530(4,0xf);
    *param_1 = *param_1 & 0xfdffffff;
    uVar2 = 0;
  }
  return uVar2;
}

