
undefined2 AttsCccGet(undefined1 param_1,uint param_2)

{
  undefined2 uVar1;
  int iVar2;
  
  iVar2 = attsCccGetTbl(param_1);
  if (iVar2 == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = *(undefined2 *)(iVar2 + (param_2 & 0xff) * 2);
  }
  return uVar1;
}

