
int FUN_0047f7ae(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  uint *puVar2;
  int iVar3;
  int iVar4;
  uint local_28;
  uint *local_24;
  uint local_20;
  undefined4 local_1c;
  undefined4 local_18;
  uint local_14;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar3 = FUN_0047ef18(&local_24,param_1);
  if (iVar3 == 0) {
    if ((*local_24 & local_20) == 0) {
      iVar3 = 0;
    }
    else {
      if (param_1 == 0x1d) {
        if (((*DAT_00480100 & 0xff) < 0x22) && (*DAT_0047fae0 << 10 < 0)) {
          return 3;
        }
        local_28 = 1;
        iVar4 = FUN_00480826(DAT_00480108,DAT_00480104,1,0);
        iVar3 = 0;
        if (iVar4 != 0) {
          return iVar4;
        }
      }
      if (param_1 == 0x1c) {
        *DAT_0048010c = *DAT_0048010c & 0xfeffffff;
        puVar2 = DAT_00480110;
        *DAT_00480110 = *DAT_00480110 & 0xfffffffe;
        *puVar2 = *puVar2 & 0xfffffff1;
      }
      FUN_0048032c();
      local_14 = FUN_00473940();
      *local_24 = *local_24 & ~local_20;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_14 & 1) == 1);
      }
      iVar4 = FUN_0047f6f2(param_1);
      if (iVar4 != 0) {
        local_28 = 0;
        iVar3 = FUN_00480826(5,local_1c,local_18,local_18);
        if (iVar3 == 0) {
          if (param_1 == 0x17) {
            FUN_004c4530(4,0x17);
          }
          if (param_1 == 0x14) {
            local_28 = local_28 & 0xffffff00;
            if (*DAT_0047fac0 == '\x03') {
              FUN_0047f11c(0);
              *DAT_00480004 = 3;
            }
            else {
              *DAT_00480004 = 0;
            }
            FUN_00480312(1,1,&local_28);
            FUN_004c45a4(0x14);
          }
          else {
            if ((param_1 < 0x1e) && ((local_20 & 0x3fffffff) != 0)) {
              FUN_00480312(3,0,&local_18);
            }
            if ((0x1d < param_1) && ((local_20 & 0x4c4) != 0)) {
              FUN_00480312(4,0,&local_18);
            }
          }
        }
      }
      FUN_00480342();
    }
  }
  return iVar3;
}

