
int FUN_005ea67a(int param_1)

{
  int *piVar1;
  undefined4 uVar2;
  undefined1 auStack_14 [4];
  int local_10;
  
  FUN_0043c0e4(auStack_14,8,0);
  piVar1 = DAT_005eb288;
  if (((param_1 != 0) && (*(char *)(param_1 + 2) != '\0')) && (*DAT_005eb288 != 0)) {
    uVar2 = FUN_005ea2c2();
    FUN_00489546(auStack_14,param_1 + 2,*piVar1,0,uVar2,0x21a,0);
    if (local_10 < 0x1c) {
      local_10 = 0x1c;
    }
    return ((local_10 + 0x1b) / 0x1c) * 0x1c;
  }
  return 0x1c;
}

