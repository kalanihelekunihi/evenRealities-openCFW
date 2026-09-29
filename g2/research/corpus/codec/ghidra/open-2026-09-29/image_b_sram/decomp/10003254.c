
void FUN_10003254(void)

{
  uint uVar1;
  
  FUN_10009934(PTR_s__AB_dmic___d_Channel__10003284,2);
  uVar1 = ((*(ushort *)(DAT_10003288 + 0x20) & 0x1ff) >> 6) - 1;
  if (uVar1 < 9) {
    FUN_10009934(PTR_s__AB_dmic_Ain_gain___d_dB__10003290,
                 *(undefined4 *)(PTR_DAT_1000328c + uVar1 * 4));
    return;
  }
  FUN_10009934(PTR_s__AB_dmic_Ain_gain___d_dB__10003290,0);
  return;
}

