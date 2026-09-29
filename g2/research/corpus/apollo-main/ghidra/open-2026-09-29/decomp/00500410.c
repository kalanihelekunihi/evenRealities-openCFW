
undefined * watchface_ops_for_kind(byte param_1)

{
  undefined *puVar1;
  
  puVar1 = PTR_PTR_005007cc;
  if ((param_1 != 1) &&
     ((param_1 == 0 ||
      (((puVar1 = PTR_PTR_005007d4, param_1 != 3 && (puVar1 = PTR_PTR_005007d0, 2 < param_1)) &&
       (puVar1 = PTR_PTR_005007d8, param_1 != 4)))))) {
    puVar1 = (undefined *)0x0;
  }
  return puVar1;
}

