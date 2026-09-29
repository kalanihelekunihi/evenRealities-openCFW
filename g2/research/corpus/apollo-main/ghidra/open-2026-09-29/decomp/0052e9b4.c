
int FUN_0052e9b4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 auStack_120 [6];
  char local_11a;
  undefined1 local_110;
  undefined1 local_10f;
  undefined1 local_10e;
  undefined1 local_10d;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  FUN_0043c0e4(&local_110,0x100,0);
  FUN_0048949c(auStack_120,0x10);
  FUN_004733ee(DAT_0052f230);
  local_110 = 1;
  local_10f = 6;
  local_10e = 0xfd;
  local_10d = 0;
  iVar1 = FUN_0052e612(param_1,&local_110,4,auStack_120);
  if ((iVar1 == 0) && (local_11a != '\0')) {
    iVar1 = 0xf;
  }
  return iVar1;
}

