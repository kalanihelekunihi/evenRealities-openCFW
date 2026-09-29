
int parse_hex4(int param_1)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = 0;
  uVar2 = 0;
  do {
    if (3 < uVar2) {
      return iVar1;
    }
    if (*(byte *)(param_1 + uVar2) - 0x30 < 10) {
      iVar1 = iVar1 + (uint)*(byte *)(param_1 + uVar2) + -0x30;
    }
    else if (*(byte *)(param_1 + uVar2) - 0x41 < 6) {
      iVar1 = iVar1 + (uint)*(byte *)(param_1 + uVar2) + -0x37;
    }
    else {
      if (5 < *(byte *)(param_1 + uVar2) - 0x61) {
        return 0;
      }
      iVar1 = iVar1 + (uint)*(byte *)(param_1 + uVar2) + -0x57;
    }
    if (uVar2 < 3) {
      iVar1 = iVar1 << 4;
    }
    uVar2 = uVar2 + 1;
  } while( true );
}

