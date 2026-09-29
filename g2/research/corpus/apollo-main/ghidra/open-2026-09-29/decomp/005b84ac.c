
undefined8 FUN_005b84ac(int *param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piStack_20;
  undefined2 *puStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  piStack_20 = param_1;
  puStack_1c = param_2;
  if ((((param_1 != (int *)0x0) && (*param_1 != 0)) && (param_1[1] != 0)) &&
     ((uStack_18 = param_3, uStack_14 = param_4, iVar1 = FUN_0043e2ea(*param_1), iVar1 != 0 &&
      (iVar1 = FUN_0043e2ea(param_1[1]), iVar1 != 0)))) {
    iVar1 = FUN_0050f810(*param_2);
    if (iVar1 != 0) {
      FUN_00498680(*param_1,iVar1);
    }
    FUN_0043c0e4(&piStack_20,0x10,0);
    if (*(int *)(param_2 + 4) == 0) {
      FUN_0044b728(&piStack_20,0x10,&DAT_005b87d8);
    }
    else if (*(int *)(param_2 + 6) == 1) {
      FUN_0044b728(&piStack_20,0x10,PTR_DAT_005b89d8,(int)*(float *)(param_2 + 2));
    }
    else {
      FUN_0044b728(&piStack_20,0x10,PTR_DAT_005b89dc,
                   (int)(longlong)(DAT_005b87e4 + (double)*(float *)(param_2 + 2) * DAT_005b87dc));
    }
    FUN_0049942e(param_1[1],&piStack_20);
    FUN_005b7a4c(param_1);
  }
  return CONCAT44(puStack_1c,piStack_20);
}

