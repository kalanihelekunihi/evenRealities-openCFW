
undefined8
semantic_CodecReadBootHeader
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_2 = 0x1a5;
    FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_00579648,0x1a5,DAT_00579644,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0057964c,DAT_0057964c);
  }
  iVar1 = DAT_00579658;
  if ((*DAT_00578c58 == 0) || (*DAT_00578c54 < 0x20)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x1a8;
      FUN_0043d574(1,DAT_00579164,DAT_00579160,DAT_00579648,0x1a8,DAT_00579650);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00579654,DAT_00579654);
    }
    uVar2 = 0xffffffff;
  }
  else {
    FUN_00439be4(DAT_00579658,*DAT_00578c58,0x20);
    uVar2 = semantic_CodecHostToBigEndian32(*(undefined4 *)(iVar1 + 8));
    *(undefined4 *)(iVar1 + 8) = uVar2;
    uVar2 = semantic_CodecHostToBigEndian32(*(undefined4 *)(iVar1 + 0xc));
    *(undefined4 *)(iVar1 + 0xc) = uVar2;
    uVar2 = semantic_CodecHostToBigEndian32(*(undefined4 *)(iVar1 + 0x10));
    *(undefined4 *)(iVar1 + 0x10) = uVar2;
    uVar2 = semantic_CodecHostToBigEndian32(*(undefined4 *)(iVar1 + 0x14));
    *(undefined4 *)(iVar1 + 0x14) = uVar2;
    semantic_CodecValidateFirmwareHeader(iVar1);
    uVar2 = 0;
  }
  return CONCAT44(param_2,uVar2);
}

