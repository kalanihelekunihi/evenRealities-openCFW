
uint case_parity8_alt(uint param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  uVar1 = 0;
  do {
    uVar2 = uVar2 ^ param_1 >> (uVar1 & 0xff) & 1;
    uVar1 = uVar1 + 1;
  } while ((int)uVar1 < 8);
  return uVar2;
}

