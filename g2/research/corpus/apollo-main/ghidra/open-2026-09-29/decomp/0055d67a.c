
void FUN_0055d67a(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  iVar1 = FUN_0055d7d8(param_1,0);
  if ((iVar1 == 0) && (iVar1 = FUN_0055d588(param_1,0x7c,&local_10,1), iVar1 == 0)) {
    local_10 = local_10 & 0xffffff7f;
    local_10 = local_10 | 0x80;
    iVar1 = FUN_0055d5e2(param_1,0x7c,&local_10,1);
    if ((iVar1 == 0) && (iVar1 = FUN_0055d7d8(param_1,1), iVar1 == 0)) {
      FUN_0055d7b4(param_1);
    }
  }
  return;
}

