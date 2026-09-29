
uint FT_Get_Char_Index(int param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  if (((param_1 != 0) && (*(int *)(param_1 + 0x5c) != 0)) &&
     (uVar1 = (**(code **)(*(int *)(*(int *)(param_1 + 0x5c) + 0xc) + 0xc))(),
     *(uint *)(param_1 + 0x10) <= uVar1)) {
    uVar1 = 0;
  }
  return uVar1;
}

