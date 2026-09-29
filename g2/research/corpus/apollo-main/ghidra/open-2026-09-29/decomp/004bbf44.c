
undefined8 PB_LastTxEncodeRingConnectInfoTimeSet(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if (param_1 != 0) goto LAB_004bbf92;
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_004bc7c0;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x169;
    FUN_0043d574(3,DAT_004bc7a4,DAT_004bc7a0,DAT_004bc7c4);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_004bbf80:
    compress_log_output(0xc000000,DAT_004bc910,DAT_004bc910);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_004bbf80;
  }
  RING_ConnectPolicyReset();
LAB_004bbf92:
  return CONCAT44(unaff_r6,unaff_r5);
}

