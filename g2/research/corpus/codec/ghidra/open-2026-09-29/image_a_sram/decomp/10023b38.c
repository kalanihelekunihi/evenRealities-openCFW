
undefined4 gx8002_flash_otp_set_region(uint param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = *(int *)(*(int *)(DAT_10023b5c + 0xc) + 0x14);
  if (param_1 < *(uint *)(iVar2 + 0xc)) {
    *(uint *)(iVar2 + 0x10) = param_1 | *(uint *)(iVar2 + 0x10) & 0xfffffff8;
    uVar1 = 0;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

