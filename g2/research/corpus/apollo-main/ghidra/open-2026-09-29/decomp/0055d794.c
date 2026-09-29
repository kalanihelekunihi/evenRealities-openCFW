
void FUN_0055d794(undefined4 param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  iVar1 = FUN_0055d588(param_1,5,&local_10,1);
  if (iVar1 == 0) {
    *param_2 = (byte)local_10 & 3;
  }
  return;
}

