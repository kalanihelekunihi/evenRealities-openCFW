
undefined4 FUN_1000deb4(undefined4 *param_1)

{
  undefined4 *puVar1;
  
  puVar1 = DAT_1000decc;
  *DAT_1000decc = *param_1;
  puVar1[1] = param_1[1];
  puVar1[2] = param_1[2];
  puVar1[3] = param_1[3];
  return 0;
}

