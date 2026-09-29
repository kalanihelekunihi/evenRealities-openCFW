
char FUN_004b0f50(undefined4 param_1,char param_2,int param_3,uint param_4)

{
  char cVar1;
  int iVar2;
  uint *puVar3;
  int local_1c;
  undefined1 local_18;
  undefined3 uStack_17;
  uint uStack_14;
  
  local_1c = (uint)(param_2 == '\0') << 0x18;
  _local_18 = CONCAT31((int3)((uint)param_3 >> 8),1);
  uStack_14 = param_4;
  cVar1 = FUN_00488f9c(param_3,param_1,&local_1c,param_4,param_1);
  if (cVar1 == '\x01') {
    if (*(int *)(param_3 + 0x2c) == 0) {
      FUN_0048908c(param_3);
      FUN_0044d25c(2,DAT_004b1054,0x2cb,DAT_004b10b0,DAT_004b10b4);
      cVar1 = '\0';
    }
    else {
      puVar3 = *(uint **)(param_3 + 0x2c);
      iVar2 = FUN_004b05a4(*puVar3 >> 8 & 0xff);
      if (iVar2 == -1) {
        FUN_0048908c(param_3);
        FUN_0044d25c(2,DAT_004b1054,0x2d5,DAT_004b10b0,DAT_004b10b8);
        cVar1 = '\0';
      }
      else if ((((param_4 & 0xff) == 0) || ((*puVar3 & 0xffff) >> 8 == 0xe)) ||
              ((*puVar3 & 0xffff) >> 8 == 6)) {
        cVar1 = '\x01';
      }
      else {
        FUN_0044d25c(2,DAT_004b1054,0x2db,DAT_004b10b0,DAT_004b10bc);
        FUN_0048908c(param_3);
        cVar1 = '\0';
      }
    }
  }
  else {
    FUN_0044d25c(3,DAT_004b1054,0x2c4,DAT_004b10b0,DAT_004b10ac);
  }
  return cVar1;
}

