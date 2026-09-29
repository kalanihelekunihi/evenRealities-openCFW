
undefined8 FUN_00492032(int param_1,int param_2,ushort param_3,undefined2 *param_4)

{
  undefined1 uVar1;
  undefined2 uVar2;
  int iVar3;
  ushort uVar4;
  
  iVar3 = 0;
  for (uVar4 = 0; uVar4 < param_3; uVar4 = uVar4 + 1) {
    uVar1 = *(undefined1 *)(param_2 + (uint)uVar4);
    *(undefined1 *)(param_1 + iVar3) = uVar1;
    iVar3 = iVar3 + 1;
    uVar2 = FUN_00491730(*param_4,uVar1);
    *param_4 = uVar2;
  }
  return CONCAT44(param_4,iVar3);
}

