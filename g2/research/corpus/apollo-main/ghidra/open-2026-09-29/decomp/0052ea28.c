
int FUN_0052ea28(int param_1,undefined4 param_2,int param_3,uint param_4)

{
  int iVar1;
  undefined1 auStack_220 [6];
  char local_21a;
  undefined1 auStack_219 [253];
  undefined1 local_11c;
  undefined1 local_11b;
  undefined1 local_11a;
  undefined1 local_119;
  undefined1 local_118;
  undefined1 local_117;
  undefined1 local_116;
  undefined1 local_115;
  undefined1 local_114;
  uint uStack_1c;
  
  uStack_1c = param_4;
  FUN_0043c0e4(&local_11c,0x100,0);
  if ((param_1 == 0) || (param_3 == 0)) {
    iVar1 = 1;
  }
  else {
    local_11c = 1;
    local_11b = 1;
    local_11a = 0xfd;
    local_119 = 5;
    local_118 = (undefined1)param_2;
    local_117 = (undefined1)((uint)param_2 >> 8);
    local_116 = (undefined1)((uint)param_2 >> 0x10);
    local_115 = (undefined1)((uint)param_2 >> 0x18);
    local_114 = (undefined1)param_4;
    FUN_0048949c(auStack_220,0x104);
    iVar1 = FUN_0052e612(param_1,&local_11c,9,auStack_220);
    if (iVar1 == 0) {
      if (local_21a == '\0') {
        FUN_00439be4(param_3,auStack_219,param_4 & 0xff);
      }
      else {
        FUN_004733ee(DAT_0052f234,local_21a);
        iVar1 = 0xf;
      }
    }
  }
  return iVar1;
}

