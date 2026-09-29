
void als_function_05(undefined4 param_1)

{
  uint *puVar1;
  
  puVar1 = DAT_004ae3bc;
  *DAT_004ae3bc = (*DAT_004ae3bc + 1) % 0x14;
  *(undefined4 *)(DAT_004ae3c0 + *puVar1 * 4) = param_1;
  *DAT_004ae3c4 = *DAT_004ae3c4 + 1;
  return;
}

