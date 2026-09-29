
undefined4 FUN_004ac776(undefined1 *param_1)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  
  puVar1 = DAT_004acafc;
  if (param_1 == (undefined1 *)0x0) {
    uVar2 = 0xffffffff;
  }
  else {
    *param_1 = *DAT_004acafc;
    param_1[1] = puVar1[1];
    param_1[2] = puVar1[2];
    param_1[3] = puVar1[3];
    uVar2 = 0;
  }
  return uVar2;
}

