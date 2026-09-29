
undefined8 FUN_004cbf38(int param_1,uint *param_2,uint param_3,undefined1 *param_4)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint *local_20;
  uint uStack_1c;
  undefined1 *local_18;
  
  uStack_1c = param_3;
  local_18 = param_4;
  if ((param_3 & 0xffff) == 0x3ff) {
    FUN_0048d540(param_4 + 8,&DAT_004cc1d4);
    *param_4 = 2;
    iVar2 = 0;
    local_20 = param_2;
  }
  else {
    iVar2 = FUN_004cb3c8(param_1,param_2,DAT_004ccb6c,
                         *(int *)(param_1 + 0x70) + 1U | (param_3 & 0xffff) << 10);
    local_20 = (uint *)(param_4 + 8);
    if (-1 < iVar2) {
      uVar1 = FUN_004cae98();
      *param_4 = uVar1;
      iVar2 = FUN_004cb3c8(param_1,param_2,DAT_004cc1dc,DAT_004ccb70 | (param_3 & 0xffff) << 10);
      local_20 = &uStack_1c;
      if (-1 < iVar2) {
        FUN_004cafea(&uStack_1c);
        iVar3 = FUN_004cae98(iVar2);
        if (iVar3 == 0x202) {
          *(undefined1 **)(param_4 + 4) = local_18;
        }
        else {
          iVar3 = FUN_004cae98(iVar2);
          if (iVar3 == 0x201) {
            uVar4 = FUN_004caeb8(iVar2);
            *(undefined4 *)(param_4 + 4) = uVar4;
          }
        }
        iVar2 = 0;
      }
    }
  }
  return CONCAT44(local_20,iVar2);
}

