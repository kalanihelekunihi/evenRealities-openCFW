
undefined4 AttsCccSet(undefined1 param_1,uint param_2,undefined2 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = attsCccGetTbl(param_1);
  if (iVar1 != 0) {
    *(undefined2 *)(iVar1 + (param_2 & 0xff) * 2) = param_3;
  }
  return param_4;
}

