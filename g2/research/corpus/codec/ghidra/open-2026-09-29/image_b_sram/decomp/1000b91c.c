
undefined4 FUN_1000b91c(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = DAT_1000b950;
  uVar2 = FUN_10009f2c(0xa800);
  *(undefined4 *)(iVar1 + 8) = uVar2;
  uVar2 = FUN_10009f80();
  iVar3 = FUN_1000e384(uVar2,*(undefined4 *)(iVar1 + 8),0xa800);
  *(int *)(iVar1 + 0xc) = iVar3;
  if (iVar3 != 0) {
    return 0;
  }
  FUN_10009934(PTR_s__LVP_MODE_DENOISE_ImcraStateInit_1000b954);
  return 0xffffffff;
}

