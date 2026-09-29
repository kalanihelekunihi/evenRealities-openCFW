
uint FUN_005e4cec(undefined1 param_1,char param_2,undefined1 param_3)

{
  uint uVar1;
  
  uVar1 = (uint)CONCAT11(param_3,param_1);
  if (param_2 != '\0') {
    uVar1 = uVar1 | 0x80000000;
  }
  return uVar1;
}

