
bool FUN_00489460(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined1 auStack_28 [4];
  undefined4 local_24;
  undefined1 local_20;
  undefined4 uStack_10;
  
  local_20 = *(undefined1 *)(param_1 + 4);
  local_24 = param_1[3];
  uStack_10 = param_4;
  iVar1 = FUN_004d4dca(param_1[0x10],auStack_28,0);
  if (iVar1 != 0) {
    iVar2 = FUN_004d5396(iVar1);
    param_1[0xb] = *(undefined4 *)(iVar2 + 0xc);
    *param_1 = *(undefined4 *)(iVar2 + 0x10);
    param_1[0x11] = iVar1;
  }
  return iVar1 != 0;
}

