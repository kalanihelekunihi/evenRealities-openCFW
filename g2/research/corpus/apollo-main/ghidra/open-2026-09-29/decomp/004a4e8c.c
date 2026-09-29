
longlong semantic_set_motion_threshold(undefined4 param_1)

{
  undefined4 *puVar1;
  uint unaff_r7;
  uint in_fpscr;
  undefined4 uVar2;
  double dVar3;
  
  puVar1 = DAT_004a56cc;
  *DAT_004a56cc = param_1;
  dVar3 = (double)VectorSignedToFloat(*puVar1,(byte)(in_fpscr >> 0x16) & 3);
  uVar2 = FUN_0050968c((float)((dVar3 * DAT_004a50ec) / DAT_004a50f4));
  *(undefined4 *)(DAT_004a5b70 + 0x38) = uVar2;
  return (ulonglong)unaff_r7 << 0x20;
}

