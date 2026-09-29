
void FUN_0055edca(int param_1,int param_2,uint param_3)

{
  undefined2 uVar1;
  int iVar2;
  uint local_10;
  
  local_10 = param_3;
  iVar2 = FUN_0055ea94(param_1,param_2,param_3 & 0xff);
  if (iVar2 == DAT_0055ee50) {
    *(undefined1 *)(param_1 + param_2 + 0xc4) = (undefined1)local_10;
    uVar1 = FUN_0055ea54(param_2);
    FUN_0055fc2c(*(undefined4 *)(param_1 + 4),uVar1,&local_10,1);
  }
  return;
}

