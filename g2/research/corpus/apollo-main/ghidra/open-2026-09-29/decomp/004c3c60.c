
undefined8 FUN_004c3c60(undefined1 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 local_10;
  
  local_10 = param_4;
  if (*(int *)(DAT_004c43e8 + 0xc) == 0) {
    uVar2 = 7;
  }
  else {
    iVar3 = FUN_004c37a8(1,param_1);
    if (iVar3 == 0) {
      local_10 = FUN_00473940();
      FUN_004c37fe(1,param_1,1);
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_10 & 1) == 1);
      }
      uVar2 = 0;
    }
    else {
      uVar2 = 0;
    }
  }
  return CONCAT44(local_10,uVar2);
}

