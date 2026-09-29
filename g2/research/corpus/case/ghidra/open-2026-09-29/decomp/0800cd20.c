
int FUN_0800cd20(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  iVar3 = 0;
  FUN_0800ac84();
  piVar1 = DAT_0800cd70;
  if (*DAT_0800cd70 != 0) {
    local_10 = 0;
    local_14 = 0;
    FUN_0800bf6c(&local_10,&local_14,&local_18);
    iVar2 = FUN_0800ca06(DAT_0800cd7c,s_Tmr_Svc_0800cd74,local_18,0,2,local_14,local_10);
    piVar1[1] = iVar2;
    if (iVar2 != 0) {
      iVar3 = 1;
    }
  }
  if (iVar3 != 0) {
    return iVar3;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

