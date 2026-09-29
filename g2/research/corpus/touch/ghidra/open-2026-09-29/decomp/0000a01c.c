
int Cy_SysClk_PeriphSetFracDivider(int param_1,int param_2,uint param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_0000a0b0;
  if ((((param_1 == 2) && (param_2 == 0)) && (param_3 < 0x10000)) && (param_4 < 0x20)) {
    *(uint *)(DAT_0000a0b0 + 0x400) =
         param_3 << 8 & DAT_0000a0b8 | *(uint *)(DAT_0000a0b0 + 0x400) & DAT_0000a0b4;
    *(uint *)(iVar1 + 0x400) = (param_4 & 0x1f) << 3 | *(uint *)(iVar1 + 0x400) & 0xffffff07;
    iVar2 = param_2;
  }
  else {
    iVar2 = DAT_0000a0ac;
    if (((param_1 == 3) && (param_2 == 0)) && ((param_3 < 0x1000000 && (param_4 < 0x20)))) {
      *(uint *)(DAT_0000a0b0 + 0x500) = param_3 << 8 | *(uint *)(DAT_0000a0b0 + 0x500) & 0xff;
      *(uint *)(iVar1 + 0x500) = *(uint *)(iVar1 + 0x500) & 0xffffff07 | (param_4 & 0x1f) << 3;
      iVar2 = param_2;
    }
  }
  return iVar2;
}

