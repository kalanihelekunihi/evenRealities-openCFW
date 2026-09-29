
undefined4 cff_size_get_globals_funcs(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int *piVar3;
  
  piVar3 = *(int **)(*(int *)(*param_1 + 0x2a4) + 0xc08);
  iVar1 = FT_Get_Module(*(undefined4 *)(*(int *)(*param_1 + 0x60) + 4),DAT_005b0004);
  if (((iVar1 == 0) || (piVar3 == (int *)0x0)) || (*piVar3 == 0)) {
    uVar2 = 0;
  }
  else {
    uVar2 = (*(code *)*piVar3)();
  }
  return uVar2;
}

