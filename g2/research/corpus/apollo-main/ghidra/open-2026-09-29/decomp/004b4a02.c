
undefined8 hciDrvWrite(undefined1 param_1,ushort param_2,int param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  uint uVar3;
  
  piVar1 = DAT_004b4d90;
  if (DAT_004b4d90[2] == DAT_004b4d90[3]) {
    error_check(0x9000000);
  }
  else if (param_2 < 0x103) {
    piVar2 = (int *)(DAT_004b4d90[5] + *DAT_004b4d90);
    *piVar2 = param_2 + 1;
    *(undefined1 *)(piVar2 + 1) = param_1;
    for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
      *(undefined1 *)((int)piVar2 + uVar3 + 5) = *(undefined1 *)(param_3 + uVar3);
    }
    FUN_00530084(piVar1,0,1);
    WsfSetEvent(*DAT_004b4da4,1);
  }
  else {
    error_check(DAT_004b4da0);
  }
  return CONCAT44(param_4,(uint)param_2);
}

