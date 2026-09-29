
byte FUN_0050361c(int param_1)

{
  int iVar1;
  byte bVar2;
  int iVar3;
  
  bVar2 = 0;
  iVar3 = DAT_005040bc;
  do {
    if (9 < bVar2) {
      return bVar2;
    }
    iVar1 = FUN_00536a00();
    if (iVar1 == 0) {
      if (*(char *)(iVar3 + 6) == *(char *)(param_1 + 6)) {
        iVar1 = FUN_004d294a(iVar3,param_1 + 7);
        goto joined_r0x00503666;
      }
    }
    else if (*(char *)(iVar3 + 6) == *(char *)(param_1 + 0xb)) {
      iVar1 = FUN_004d294a(iVar3,param_1 + 0xc);
joined_r0x00503666:
      if (iVar1 != 0) {
        return bVar2;
      }
    }
    bVar2 = bVar2 + 1;
    iVar3 = iVar3 + 0xf;
  } while( true );
}

