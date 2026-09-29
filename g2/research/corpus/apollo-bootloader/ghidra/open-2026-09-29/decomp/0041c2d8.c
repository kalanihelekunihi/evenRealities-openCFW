
int FUN_0041c2d8(uint param_1,undefined1 *param_2,uint *param_3,uint param_4)

{
  int iVar1;
  uint uStack_18;
  undefined1 *puStack_14;
  uint *local_10;
  uint local_c;
  
  if (param_2 == (undefined1 *)0x0) {
    iVar1 = 6;
  }
  else {
    *param_2 = 0;
    uStack_18 = param_1;
    puStack_14 = param_2;
    local_10 = param_3;
    local_c = param_4;
    iVar1 = FUN_0041b8f8(&uStack_18,param_1 & 0xff);
    if (iVar1 == 0) {
      *param_2 = (*local_10 & local_c) != 0;
      iVar1 = 0;
    }
  }
  return iVar1;
}

