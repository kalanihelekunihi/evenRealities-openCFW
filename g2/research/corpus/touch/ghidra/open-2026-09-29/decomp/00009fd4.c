
undefined4 Cy_SysClk_PeriphSetDivider(int param_1,uint param_2,uint param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = DAT_0000a00c;
  if (((param_1 == 1) && (param_2 < 2)) && (param_3 < 0x10000)) {
    iVar2 = (param_2 + 0xc0) * 4;
    *(uint *)(iVar2 + DAT_0000a010) =
         *(uint *)(iVar2 + DAT_0000a010) & DAT_0000a014 | param_3 << 8 & DAT_0000a018;
    uVar1 = 0;
  }
  return uVar1;
}

