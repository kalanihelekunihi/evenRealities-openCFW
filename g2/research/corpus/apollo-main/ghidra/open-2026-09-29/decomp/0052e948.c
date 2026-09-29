
int FUN_0052e948(undefined4 param_1,undefined1 param_2,undefined1 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 auStack_128 [6];
  char local_122;
  undefined1 local_118;
  undefined1 local_117;
  undefined1 local_116;
  undefined1 local_115;
  undefined1 local_114;
  undefined1 local_113;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  FUN_0043c0e4(&local_118,0x100,0);
  FUN_0048949c(auStack_128,0x10);
  local_118 = 1;
  local_117 = 7;
  local_116 = 0xfd;
  local_115 = 2;
  local_114 = param_2;
  local_113 = param_3;
  iVar1 = FUN_0052e612(param_1,&local_118,6,auStack_128);
  if ((iVar1 == 0) && (local_122 != '\0')) {
    iVar1 = 0xf;
  }
  return iVar1;
}

