
void AttsSetSignCounter(undefined1 param_1,undefined4 param_2)

{
  undefined4 *puVar1;
  
  puVar1 = (undefined4 *)attsSignCcbByConnId(param_1);
  *puVar1 = param_2;
  return;
}

