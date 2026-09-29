
undefined4 FUN_005d2e0c(int param_1,undefined4 param_2,int param_3,undefined4 *param_4)

{
  char cVar1;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 *puStack_1c;
  
  local_28 = 0;
  local_24 = *(undefined4 *)(param_3 + 0x10);
  local_20 = *(undefined4 *)(param_3 + 0x14);
  puStack_1c = param_4;
  FUN_005d2bae(param_1,param_3);
  if (*(int *)(param_1 + 4) == 0) {
    *(undefined1 *)(param_1 + 0xec) = 0;
    cVar1 = *(char *)(param_1 + 0xb9);
    while( true ) {
      FUN_005d350c(param_1 + 0x90);
      FUN_005d4ed0(param_1,param_2,param_1 + 0x90,&local_24,0,0,0,&local_28);
      if (*(int *)(param_1 + 4) != 0) break;
      if ((cVar1 == '\0') || (-1 < *(int *)(param_1 + 0xa0))) {
        FUN_005d351c(param_1 + 0x90);
        break;
      }
      *(undefined1 *)(param_1 + 0xec) = 1;
      cVar1 = '\0';
    }
  }
  *param_4 = local_28;
  FUN_005d2a0a(param_1 + 4,0);
  return *(undefined4 *)(param_1 + 4);
}

