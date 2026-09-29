
undefined8 FUN_0052ed34(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint local_18;
  undefined4 uStack_14;
  
  uVar1 = DAT_0052f250;
  local_18 = 0;
  uStack_14 = param_4;
  iVar2 = FUN_0052ea28(param_1,DAT_0052f250,&local_18,4);
  if (iVar2 == 0) {
    local_18 = local_18 & 0xffffe0ff;
    iVar2 = FUN_0052eaf8(param_1,uVar1,&local_18,4);
    uVar1 = DAT_0052f254;
    if (iVar2 == 0) {
      iVar2 = FUN_0052ea28(param_1,DAT_0052f254,&local_18,4);
      if (iVar2 == 0) {
        local_18 = DAT_0052f258;
        iVar2 = FUN_0052eaf8(param_1,uVar1,&local_18,4);
        if (iVar2 == 0) {
          FUN_004733ee(DAT_0052f25c);
        }
        else {
          FUN_004733ee(DAT_0052f260,iVar2);
        }
      }
      else {
        FUN_004733ee(DAT_0052f264,iVar2);
      }
    }
    else {
      FUN_004733ee(DAT_0052f268,iVar2);
    }
  }
  else {
    FUN_004733ee(DAT_0052f26c,iVar2);
  }
  return CONCAT44(local_18,iVar2);
}

