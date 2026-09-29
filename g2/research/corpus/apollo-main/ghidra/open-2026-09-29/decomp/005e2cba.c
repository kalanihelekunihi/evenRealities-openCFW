
undefined8 smpScActJwncCalcG2(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_18;
  
  iVar1 = SmpScAlloc(0x50,param_1,param_2);
  local_18 = param_3;
  if (iVar1 != 0) {
    if (*(char *)(param_1 + 0x3a) == '\0') {
      uVar2 = SmpScCat(iVar1,*(undefined4 *)(*(int *)(param_1 + 0x48) + 8),0x20);
      uVar2 = SmpScCat(uVar2,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc),0x20);
    }
    else {
      uVar2 = SmpScCat(iVar1,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc),0x20);
      uVar2 = SmpScCat(uVar2,*(undefined4 *)(*(int *)(param_1 + 0x48) + 8),0x20);
    }
    SmpScCat128(uVar2,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10);
    SmpScCmac(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14),iVar1,0x50,param_1);
    local_18 = param_2;
  }
  return CONCAT44(param_4,local_18);
}

