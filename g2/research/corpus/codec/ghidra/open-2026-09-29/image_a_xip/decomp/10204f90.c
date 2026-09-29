
undefined4 gx8002_aout_set_db(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = (uint)(param_2 < 0x12) * 0x12 + (uint)(param_2 >= 0x12) * 0x12;
  iVar1 = 0;
  iVar3 = 0x25;
  do {
    if ((uint)(iVar2 < -0x12) * -0x12 + (uint)(iVar2 >= -0x12) * iVar2 ==
        (int)*(short *)(iRam10204fec + iVar1 * 4 + 2)) break;
    iVar1 = iVar1 + 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  uRam00000014 = (*(ushort *)(iRam10204fec + iVar1 * 4) & 0x3ff) << 0x10 | uRam00000014;
  *(short *)(param_1 + 0x12) = (short)param_2;
  return 0;
}

