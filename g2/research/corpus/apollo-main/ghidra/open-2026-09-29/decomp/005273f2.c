
undefined8 FT_Get_Module_Interface(void)

{
  int *piVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  piVar1 = (int *)FT_Get_Module();
  if (piVar1 == (int *)0x0) {
    uVar2 = 0;
  }
  else {
    uVar2 = *(undefined4 *)(*piVar1 + 0x14);
  }
  return CONCAT44(unaff_r7,uVar2);
}

