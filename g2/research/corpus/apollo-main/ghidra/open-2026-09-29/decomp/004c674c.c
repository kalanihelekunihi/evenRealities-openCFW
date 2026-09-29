
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 device_mgr_fn_004c674c(void)

{
  byte *pbVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  if (0xce4 < *(int *)(DAT_004c6ca0 + 8)) {
    pbVar1 = (byte *)FUN_0050938e(1);
    if ((*pbVar1 < 4) ||
       ((((iVar2 = productModeGet(), iVar2 != 1 && (*DAT_004c6ca4 == '\0')) &&
         (iVar2 = FUN_004ac75a(), iVar2 != 1)) &&
        ((iVar2 = semantic_OtaTransferActive(), iVar2 == 0 && (*_DAT_004c6ca8 == '\0')))))) {
      device_mgr_fn_004c67a4(1);
    }
    else {
      device_mgr_fn_004c67a4(0);
    }
  }
  return unaff_r7;
}

