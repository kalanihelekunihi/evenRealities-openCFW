
int FUN_0052e6ac(undefined4 param_1,undefined4 param_2,undefined4 param_3,int *param_4)

{
  int iVar1;
  undefined1 auStack_128 [6];
  char local_122;
  byte local_121;
  byte local_120;
  byte local_11f;
  byte local_11e;
  undefined1 local_118;
  undefined1 local_117;
  undefined1 local_116;
  undefined1 local_115;
  undefined1 local_114;
  undefined1 local_113;
  undefined1 local_112;
  undefined1 local_111;
  undefined1 local_110;
  undefined1 local_10f;
  undefined1 local_10e;
  undefined1 local_10d;
  
  FUN_0043c0e4(&local_118,0x100,0);
  FUN_0048949c(auStack_128,0x10);
  local_118 = 1;
  local_117 = 0x4e;
  local_116 = 0xfc;
  local_115 = 8;
  local_114 = (undefined1)param_2;
  local_113 = (undefined1)((uint)param_2 >> 8);
  local_112 = (undefined1)((uint)param_2 >> 0x10);
  local_111 = (undefined1)((uint)param_2 >> 0x18);
  local_110 = (undefined1)param_3;
  local_10f = (undefined1)((uint)param_3 >> 8);
  local_10e = (undefined1)((uint)param_3 >> 0x10);
  local_10d = (undefined1)((uint)param_3 >> 0x18);
  iVar1 = FUN_0052e612(param_1,&local_118,0xc,auStack_128);
  if (iVar1 == 0) {
    if (local_122 == '\0') {
      *param_4 = (uint)local_120 * 0x100 + (uint)local_121 + (uint)local_11f * 0x10000 +
                 (uint)local_11e * 0x1000000;
    }
    else {
      FUN_004733ee(DAT_0052f210,local_122,param_2);
      iVar1 = 0xf;
    }
  }
  return iVar1;
}

