
undefined8 semantic_OtaTransferActive(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  iVar1 = UX_GetSelfOTAStatus();
  if ((iVar1 == 1) || (iVar1 = UX_GetPeerOTAStatus(), iVar1 == 1)) {
    uVar2 = 1;
  }
  else if (*DAT_00448878 == '\x01') {
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(unaff_r7,uVar2);
}

