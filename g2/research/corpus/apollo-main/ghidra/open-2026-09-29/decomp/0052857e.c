
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
raccess_guess_darwin_hfsplus
          (undefined4 *param_1,undefined4 param_2,undefined4 param_3,int *param_4,
          undefined4 *param_5)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int *piStack_20;
  
  piStack_20 = param_4;
  iVar1 = FUN_0044a43c(param_3);
  iVar2 = ft_mem_alloc(*param_1,iVar1 + 6,&piStack_20);
  piVar3 = piStack_20;
  if (piStack_20 == (int *)0x0) {
    FUN_00439be4(iVar2,param_3,iVar1);
    FUN_00439be4(iVar1 + iVar2,_DAT_00528ed4,6);
    *param_4 = iVar2;
    *param_5 = 0;
    piVar3 = (int *)0x0;
  }
  return CONCAT44(piStack_20,piVar3);
}

