
undefined4 clkgen_config_426ccc(byte *param_1)

{
  uint *puVar1;
  uint *puVar2;
  undefined4 uVar3;
  
  if (param_1 == (byte *)0x0) {
    uVar3 = 6;
  }
  else {
    *DAT_00426d3c = *DAT_00426d3c | 7;
    puVar1 = DAT_00426d40;
    *DAT_00426d40 = *DAT_00426d40 & 0xdfffffff | (*param_1 & 1) << 0x1d;
    puVar2 = DAT_00426d44;
    *DAT_00426d44 = param_1[1] & 3 | *DAT_00426d44 & 0xfffffffc;
    *puVar2 = *puVar2 & 0x80000003 | (*(uint *)(param_1 + 4) & 0x1fffffff) << 2;
    *puVar1 = *puVar1 | 1;
    uVar3 = 0;
  }
  return uVar3;
}

