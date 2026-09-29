
int FUN_00513f9c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_18 = param_1;
  uStack_14 = param_2;
  uStack_10 = param_3;
  uStack_c = param_4;
  FUN_00514046(0xf8,0);
  FUN_00513f0c(0x1c,4);
  FUN_00513ed0(0x1c);
  piVar1 = DAT_00514250;
  if (*DAT_00514250 == 0) {
    iVar2 = FUN_00441636(1,0,3);
    *piVar1 = iVar2;
  }
  iVar2 = DAT_0051425c;
  if (*(int *)(DAT_0051425c + 0xc) == 0) {
    FUN_00514070(&uStack_18,0,0x1300);
    FUN_00439c04(iVar2,&uStack_18,0x10);
  }
  iVar2 = FUN_00523bf8(iVar2,1);
  if (iVar2 == 0) {
    *DAT_0051424c = 0xffffffff;
    iVar2 = 0;
  }
  return iVar2;
}

