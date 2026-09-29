
undefined1 FUN_005cb402(int param_1,uint param_2)

{
  undefined1 uVar1;
  uint uVar2;
  
  if (((*(uint *)(param_1 + 0x48) & 0x3fffffff) >> 0xf == 0) ||
     (uVar2 = (*(uint *)(param_1 + 0x48) & 0x3fffffff) >> 0xf, param_2 != uVar2 * (param_2 / uVar2))
     ) {
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

