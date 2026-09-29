
undefined8 FT_GlyphLoader_New(undefined4 param_1,undefined4 *param_2,undefined4 param_3,int param_4)

{
  undefined4 *puVar1;
  int local_10;
  
  local_10 = param_4;
  puVar1 = (undefined4 *)ft_mem_alloc(param_1,0x60,&local_10);
  if (local_10 == 0) {
    *puVar1 = param_1;
    *param_2 = puVar1;
  }
  return CONCAT44(local_10,local_10);
}

