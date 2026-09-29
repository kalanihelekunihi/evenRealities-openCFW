
undefined8 tt_size_run_prep(int *param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = *param_1;
  iVar2 = param_1[0x4b];
  iVar1 = TT_Load_Context(iVar2,iVar3,param_1);
  if (iVar1 == 0) {
    *(undefined4 *)(iVar2 + 0x1b0) = 0;
    *(undefined4 *)(iVar2 + 0x10) = 0;
    *(undefined1 *)(iVar2 + 0x1ec) = 0;
    *(undefined1 *)(iVar2 + 0x235) = param_2;
    TT_Set_CodeRange(iVar2,2,*(undefined4 *)(iVar3 + 0x294),*(undefined4 *)(iVar3 + 0x290));
    TT_Clear_CodeRange(iVar2,3);
    if (*(int *)(iVar3 + 0x290) == 0) {
      iVar1 = 0;
    }
    else {
      TT_Goto_CodeRange(iVar2,2,0);
      iVar1 = (**(code **)(iVar3 + 0x2a0))(iVar2);
    }
    param_1[0x4d] = iVar1;
    *(undefined2 *)(iVar2 + 0x126) = 0x4000;
    *(undefined2 *)(iVar2 + 0x128) = 0;
    *(undefined2 *)(iVar2 + 0x12a) = 0x4000;
    *(undefined2 *)(iVar2 + 300) = 0;
    *(undefined2 *)(iVar2 + 0x12e) = 0x4000;
    *(undefined2 *)(iVar2 + 0x130) = 0;
    *(undefined2 *)(iVar2 + 0x120) = 0;
    *(undefined2 *)(iVar2 + 0x122) = 0;
    *(undefined2 *)(iVar2 + 0x124) = 0;
    *(undefined2 *)(iVar2 + 0x15c) = 1;
    *(undefined2 *)(iVar2 + 0x15e) = 1;
    *(undefined2 *)(iVar2 + 0x160) = 1;
    *(undefined4 *)(iVar2 + 0x134) = 1;
    FUN_00439c04(param_1 + 0x2d,iVar2 + 0x120,0x44);
    TT_Save_Context(iVar2,param_1);
  }
  return CONCAT44(param_4,iVar1);
}

