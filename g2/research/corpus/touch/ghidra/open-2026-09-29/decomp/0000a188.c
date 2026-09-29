
undefined4 Cy_SysClk_ClkHfSetSource(uint param_1)

{
  undefined4 uVar1;
  
  uVar1 = DAT_0000a1bc;
  if ((param_1 < 3) && ((param_1 != 1 || (uVar1 = DAT_0000a1b8, *(int *)(DAT_0000a1b4 + 0x30) < 0)))
     ) {
    *(uint *)(DAT_0000a1b4 + 0x28) =
         *(uint *)(DAT_0000a1b4 + 0x28) & 0xffffffcf | (param_1 & 3) << 4;
    uVar1 = 0;
  }
  return uVar1;
}

