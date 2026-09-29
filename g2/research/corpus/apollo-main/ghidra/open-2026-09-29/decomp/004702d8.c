
int FUN_004702d8(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  FUN_0043bb00(&local_10,0,5,param_4,param_1,param_2);
  iVar1 = FUN_00470168(5,0,0,&local_10,1);
  if (iVar1 == 0) {
    if (local_10 << 0x1f < 0) {
      iVar1 = 1;
    }
    else {
      iVar1 = 0;
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00470a7c,DAT_00470a78,DAT_00470a94,0x376,DAT_00470a90);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00470a98);
    }
  }
  return iVar1;
}

