
undefined8 FUN_0044fa7e(undefined4 *param_1)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_1 == (undefined4 *)0x0) {
    param_1 = (undefined4 *)FUN_0044fa1a();
  }
  if (param_1 == (undefined4 *)0x0) {
    uVar1 = 0;
  }
  else if (((*(byte *)(param_1 + 0xbf) & 7) == 1) || ((*(byte *)(param_1 + 0xbf) & 7) == 3)) {
    uVar1 = param_1[1];
  }
  else {
    uVar1 = *param_1;
  }
  return CONCAT44(unaff_r7,uVar1);
}

