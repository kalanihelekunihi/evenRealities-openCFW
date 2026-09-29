
undefined4 FUN_005ea992(void)

{
  int iVar1;
  short sVar2;
  int iVar3;
  undefined4 in_r3;
  
  iVar1 = DAT_005eb28c;
  if (*(int *)(DAT_005eb28c + 4) != 0) {
    iVar3 = td_ring_ptr();
    if (iVar3 == 0) {
      sVar2 = 0;
    }
    else {
      sVar2 = *(short *)(iVar3 + 0x8500);
    }
    if (sVar2 == 0) {
      FUN_0044ea04(*(undefined4 *)(iVar1 + 4),0,0);
      *(undefined1 *)(iVar1 + 0x28c) = 1;
    }
    else if (*(char *)(iVar1 + 0x28c) != '\0') {
      iVar3 = FUN_0043fdda(*(undefined4 *)(iVar1 + 4));
      iVar3 = *(int *)(iVar1 + 0x1c8) - iVar3;
      if (iVar3 < 0) {
        iVar3 = 0;
      }
      FUN_0044ea04(*(undefined4 *)(iVar1 + 4),iVar3,0);
      FUN_005ea926(iVar3);
    }
  }
  return in_r3;
}

