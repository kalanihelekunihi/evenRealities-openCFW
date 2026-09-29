
undefined8 AttsGetSignCounter(undefined1 param_1)

{
  undefined4 *puVar1;
  undefined4 unaff_r7;
  
  puVar1 = (undefined4 *)attsSignCcbByConnId(param_1);
  return CONCAT44(unaff_r7,*puVar1);
}

