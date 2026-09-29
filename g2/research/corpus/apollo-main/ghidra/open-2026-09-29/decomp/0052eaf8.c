
int FUN_0052eaf8(undefined4 param_1,undefined4 param_2,undefined4 param_3,byte param_4)

{
  int iVar1;
  undefined4 local_12c;
  undefined1 auStack_128 [6];
  char local_122;
  undefined1 local_118;
  undefined1 local_117;
  undefined1 local_116;
  char local_115;
  undefined1 local_114;
  undefined1 local_113;
  undefined1 local_112;
  undefined1 local_111;
  undefined1 auStack_110 [248];
  
  FUN_0043c0e4(&local_118,0x100,0);
  local_12c = 0;
  local_118 = 1;
  local_117 = 3;
  local_116 = 0xfd;
  local_115 = param_4 + 4;
  local_114 = (undefined1)param_2;
  local_113 = (undefined1)((uint)param_2 >> 8);
  local_112 = (undefined1)((uint)param_2 >> 0x10);
  local_111 = (undefined1)((uint)param_2 >> 0x18);
  FUN_00439be4(auStack_110,param_3,param_4);
  FUN_0048949c(auStack_128,0x10);
  iVar1 = FUN_0052e612(param_1,&local_118,auStack_110 + ((uint)param_4 - (int)&local_118),
                       auStack_128,&local_12c);
  if ((iVar1 == 0) && (local_122 != '\0')) {
    FUN_004733ee(DAT_0052f234,local_122);
    iVar1 = 0xf;
  }
  return iVar1;
}

