
undefined4 FUN_005ea926(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  short sVar2;
  int iVar3;
  
  iVar1 = DAT_005eb28c;
  if (*(int *)(DAT_005eb28c + 8) != 0) {
    iVar3 = td_ring_ptr();
    if (iVar3 == 0) {
      sVar2 = 0;
    }
    else {
      sVar2 = *(short *)(iVar3 + 0x8500);
    }
    if (sVar2 != 0) {
      sVar2 = FUN_005ea8ce(param_1);
      if ((*(char *)(iVar1 + 0x1c2) == '\0') || (*(short *)(iVar1 + 0x1c0) != sVar2)) {
        FUN_005ea810(sVar2);
      }
    }
  }
  return param_4;
}

