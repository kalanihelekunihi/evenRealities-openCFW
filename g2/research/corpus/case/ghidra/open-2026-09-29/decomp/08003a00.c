
void glasses_charge_state_reset(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_08003a2c;
  if (param_1 != 0) {
    *(undefined1 *)(DAT_08003a2c + 0x34) = 0;
    *(undefined4 *)(iVar1 + 0x3c) = 0;
    *(undefined4 *)(iVar1 + 0x48) = 0;
    *(undefined2 *)(iVar1 + 0x38) = 0;
    *(undefined1 *)(iVar1 + 0x31) = 0;
    *(undefined1 *)(iVar1 + 0x12) = 1;
    return;
  }
  *(undefined1 *)(DAT_08003a2c + 0x50) = 0;
  *(undefined4 *)(iVar1 + 0x58) = 0;
  *(undefined4 *)(iVar1 + 100) = 0;
  *(undefined2 *)(iVar1 + 0x54) = 0;
  *(undefined1 *)(iVar1 + 0x4d) = 0;
  *(undefined1 *)(iVar1 + 0x13) = 1;
  return;
}

