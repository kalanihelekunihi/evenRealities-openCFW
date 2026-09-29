
undefined4
af_shaper_get_elem(int param_1,undefined4 *param_2,undefined4 param_3,int param_4,
                  undefined4 *param_5)

{
  undefined4 uVar1;
  
  uVar1 = *param_2;
  if (param_4 != 0) {
    FT_Get_Advance(**(undefined4 **)(param_1 + 0x24),uVar1,0x803);
  }
  if (param_5 != (undefined4 *)0x0) {
    *param_5 = 0;
  }
  return uVar1;
}

