
void als_function_04(undefined4 param_1)

{
  uint *puVar1;
  
  puVar1 = DAT_004ae3b4;
  *DAT_004ae3b4 = (*DAT_004ae3b4 + 1) % 5;
  *(undefined4 *)(DAT_004ae3b8 + *puVar1 * 4) = param_1;
  *DAT_004ae4cc = *DAT_004ae4cc + 1;
  return;
}

