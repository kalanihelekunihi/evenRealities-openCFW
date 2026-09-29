
int af_dummy_hints_apply(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = af_glyph_hints_reload(param_2,param_3);
  if (iVar1 == 0) {
    af_glyph_hints_save(param_2,param_3);
  }
  return iVar1;
}

