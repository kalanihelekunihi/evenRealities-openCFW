
int FUN_00544814(int param_1,undefined4 param_2,undefined4 param_3)

{
  uint local_24;
  int local_20;
  int local_1c;
  int local_18;
  undefined4 local_14;
  int *local_10;
  
  local_20 = -1;
  local_24 = 0;
  local_1c = 0;
  local_10 = &local_20;
  local_18 = param_1;
  local_14 = param_3;
  FUN_00544736(param_1,param_2,0,&local_24,&local_1c,DAT_00545260,0);
  if (local_1c != 0) {
    FUN_00544736(param_1,param_2,2,&local_18,0,DAT_0054531c,1);
  }
  if ((local_24 != 0) && (local_20 == -1)) {
    if ((local_24 < 2) && (*(char *)(param_1 + 0x30) == '\0')) {
      *(undefined1 *)(param_1 + 0x30) = 1;
    }
    else {
      FUN_00544736(param_1,param_2,1,&local_18,0,DAT_0054531c,1);
    }
  }
  return local_20;
}

