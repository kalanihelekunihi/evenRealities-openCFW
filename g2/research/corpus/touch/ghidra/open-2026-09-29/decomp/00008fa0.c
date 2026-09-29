
undefined4 Cy_MSCLP_Capture(int param_1,int param_2,char *param_3)

{
  undefined4 uVar1;
  
  uVar1 = DAT_00008fc8;
  if ((((param_1 != 0) && (param_2 != 0)) && (param_3 != (char *)0x0)) &&
     (uVar1 = DAT_00008fcc, *param_3 == '\0')) {
    *param_3 = (char)param_2;
    uVar1 = 0;
  }
  return uVar1;
}

