
undefined8 tt_size_run_fpgm(int *param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = *param_1;
  iVar3 = param_1[0x4b];
  iVar1 = TT_Load_Context(iVar3,iVar2,param_1);
  if (iVar1 == 0) {
    *(undefined4 *)(iVar3 + 0x1b0) = 0;
    *(undefined4 *)(iVar3 + 0x10) = 0;
    *(undefined4 *)(iVar3 + 0x1e0) = 0x40;
    *(undefined4 *)(iVar3 + 0x1e4) = 0;
    *(undefined4 *)(iVar3 + 0x1e8) = 0;
    *(undefined1 *)(iVar3 + 0x1ec) = 0;
    *(undefined4 *)(iVar3 + 0x238) = 0x4000;
    *(undefined1 *)(iVar3 + 0x235) = param_2;
    *(undefined2 *)(iVar3 + 0xdc) = 0;
    *(undefined2 *)(iVar3 + 0xde) = 0;
    *(undefined4 *)(iVar3 + 0xe0) = 0;
    *(undefined4 *)(iVar3 + 0xe4) = 0;
    *(undefined2 *)(iVar3 + 0x100) = 0;
    *(undefined4 *)(iVar3 + 0x108) = 0;
    *(undefined4 *)(iVar3 + 0x104) = 0x10000;
    TT_Set_CodeRange(iVar3,1,*(undefined4 *)(iVar2 + 0x28c),*(undefined4 *)(iVar2 + 0x288));
    TT_Clear_CodeRange(iVar3,2);
    TT_Clear_CodeRange(iVar3,3);
    if (*(int *)(iVar2 + 0x288) == 0) {
      iVar1 = 0;
    }
    else {
      TT_Goto_CodeRange(iVar3,1,0);
      iVar1 = (**(code **)(iVar2 + 0x2a0))(iVar3);
    }
    param_1[0x4c] = iVar1;
    if (iVar1 == 0) {
      TT_Save_Context(iVar3,param_1);
    }
  }
  return CONCAT44(param_4,iVar1);
}

