
void FUN_00522ae0(uint param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  undefined4 *puVar2;
  
  iVar1 = param_3;
  if (0 < param_3) {
    iVar1 = param_4;
  }
  if ((0 < iVar1) && (puVar2 = (undefined4 *)FUN_00514aec(3), puVar2 != (undefined4 *)0x0)) {
    *puVar2 = 0x104;
    puVar2[1] = param_1 & 0xffff | param_2 << 0x10;
    puVar2[2] = 0x108;
    puVar2[3] = param_3 + param_1 & 0xffff | (param_4 + param_2) * 0x10000;
    puVar2[4] = DAT_005232cc;
    puVar2[5] = *(uint *)(*DAT_005232d0 + 0x18) | 2;
  }
  return;
}

