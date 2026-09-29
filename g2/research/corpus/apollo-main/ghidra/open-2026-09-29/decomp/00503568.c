
undefined4 FUN_00503568(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  int iVar4;
  
  iVar1 = DAT_005040bc;
  bVar3 = 0;
  iVar4 = DAT_005040bc;
  do {
    if (9 < bVar3) {
      return param_4;
    }
    iVar2 = FUN_00536a00();
    if (iVar2 == 0) {
      if ((*(char *)(iVar4 + 6) == *(char *)(param_1 + 6)) &&
         (iVar2 = FUN_004d294a(iVar4,param_1 + 7), iVar2 != 0)) {
        return param_4;
      }
      if (*(char *)(iVar4 + 6) == -1) {
        *(undefined1 *)(iVar4 + 6) = *(undefined1 *)(param_1 + 6);
        *(undefined1 *)(iVar4 + 0xe) = *(undefined1 *)(param_1 + 0xe);
        FUN_004d293c(iVar4,param_1 + 7);
        *(undefined1 *)(iVar4 + 7) = *(undefined1 *)(param_1 + 0x14);
        FUN_004d293c(iVar4 + 8,param_1 + 0x15);
        *(char *)(iVar1 + 0x96) = *(char *)(iVar1 + 0x96) + '\x01';
        return param_4;
      }
    }
    else {
      if ((*(char *)(iVar4 + 6) == *(char *)(param_1 + 0xb)) &&
         (iVar2 = FUN_004d294a(iVar4,param_1 + 0xc), iVar2 != 0)) {
        return param_4;
      }
      if (*(char *)(iVar4 + 6) == -1) {
        *(undefined1 *)(iVar4 + 6) = *(undefined1 *)(param_1 + 0xb);
        FUN_004d293c(iVar4,param_1 + 0xc);
        *(undefined1 *)(iVar4 + 7) = *(undefined1 *)(param_1 + 0x12);
        FUN_004d293c(iVar4 + 8,param_1 + 0x13);
        *(char *)(iVar1 + 0x96) = *(char *)(iVar1 + 0x96) + '\x01';
        return param_4;
      }
    }
    bVar3 = bVar3 + 1;
    iVar4 = iVar4 + 0xf;
  } while( true );
}

