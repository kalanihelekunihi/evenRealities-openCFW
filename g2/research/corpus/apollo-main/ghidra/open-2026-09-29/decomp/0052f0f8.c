
undefined8 FUN_0052f0f8(undefined4 param_1,uint param_2,uint param_3,uint param_4)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint local_20;
  undefined4 local_1c;
  
  uVar4 = 0;
  local_20 = param_3;
  local_1c = param_4;
  FUN_0043c0e4(&local_20,8,0);
  if ((param_3 & 0xff) == 0) {
    FUN_004733ee(DAT_0052f2b8);
    iVar3 = FUN_0052f094(param_1,&local_20);
    if (iVar3 != 0) {
      FUN_004733ee(DAT_0052f2bc);
      goto LAB_0052f1f2;
    }
    uVar5 = (local_20 >> 8 & 0x1f) << 1 | local_20 >> 7 & 1;
    FUN_004733ee(DAT_0052f2c0,uVar5,param_2 & 0xff);
    if (uVar5 == (param_2 & 0xff)) {
      FUN_004733ee(DAT_0052f2c4);
      uVar4 = 0;
      goto LAB_0052f1f2;
    }
  }
  else {
    FUN_004733ee(DAT_0052f2c8);
  }
  iVar3 = FUN_0052e8be(param_1);
  if (iVar3 == 0) {
    iVar3 = FUN_0052ef74(param_1,&local_20);
    if (iVar3 == 0) {
      local_1c = local_1c & 0xffffe07f;
      bVar1 = (byte)local_1c | (byte)(param_2 << 7);
      bVar2 = local_1c._1_1_ | (byte)((param_2 & 0x3f) >> 1);
      local_1c._0_2_ = CONCAT11(bVar2,bVar1);
      iVar3 = FUN_0052efba(param_1);
      if (iVar3 == 0) {
        iVar3 = FUN_0052efec(param_1,&local_20);
        if (iVar3 == 0) {
          iVar3 = FUN_0052e4b4(param_1);
          if (iVar3 != 0) {
            FUN_004733ee(DAT_0052f2dc);
            uVar4 = 5;
          }
        }
        else {
          FUN_004733ee(DAT_0052f2d8);
        }
      }
      else {
        FUN_004733ee(DAT_0052f2d4);
      }
    }
    else {
      FUN_004733ee(DAT_0052f2d0);
    }
  }
  else {
    FUN_004733ee(DAT_0052f2cc);
    uVar4 = 1;
  }
LAB_0052f1f2:
  return CONCAT44(local_20,uVar4);
}

