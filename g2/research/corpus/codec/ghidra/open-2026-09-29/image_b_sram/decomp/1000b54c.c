
undefined4 FUN_1000b54c(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int *piVar3;
  
  piVar3 = DAT_1000b5f0;
  if (((((char)param_1[5] == '\0') || (piVar3 = DAT_1000b5f4, (char)param_1[5] == '\x01')) &&
      (piVar3[3] != 0)) && ((param_1[6] == 0 || (param_1[4] != 0)))) {
    iVar1 = FUN_1000a018(piVar3 + 0x57);
    if (iVar1 == 0) {
      *(ushort *)(param_1 + 2) =
           (ushort)(*(char *)((int)param_1 + 7) != '\0') * 4 + (short)param_1[6];
      if (*param_1 == 0) {
        *param_1 = *piVar3;
      }
      if ((*(ushort *)(param_1 + 1) & 0xff00) != 0x200) {
        iVar1 = piVar3[5];
        *(char *)(piVar3 + 5) = (char)iVar1 + '\x01';
        *(char *)((int)param_1 + 6) = (char)iVar1;
      }
      uVar2 = FUN_1000c5c4(0,param_1,10);
      *(short *)((int)param_1 + 10) = (short)uVar2;
      *(short *)(param_1 + 3) = (short)((uint)uVar2 >> 0x10);
      gx8002_dcache_clean_range(param_1,0x10);
      iVar1 = FUN_10015b64(piVar3 + 0x57,param_1);
      if (iVar1 != 0) {
        if (piVar3[6] == 0) {
          FUN_1000ab10((char)piVar3[2]);
        }
        return 0;
      }
    }
  }
  return 0xffffffff;
}

