
undefined8 FUN_00490bf8(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 uVar2;
  int *piVar3;
  
  piVar3 = (int *)**(undefined4 **)(param_2 + 0x1c);
  do {
    if (piVar3 == (int *)0x0) {
      uVar2 = 1;
LAB_00490c30:
      return CONCAT44(param_4,uVar2);
    }
    if (*(int *)(*piVar3 + 4) == 0) {
      cVar1 = FUN_00490bc8(param_1,piVar3);
    }
    else {
      cVar1 = (**(code **)(*piVar3 + 4))(param_1,piVar3);
    }
    if (cVar1 == '\0') {
      uVar2 = 0;
      goto LAB_00490c30;
    }
    piVar3 = (int *)piVar3[2];
  } while( true );
}

