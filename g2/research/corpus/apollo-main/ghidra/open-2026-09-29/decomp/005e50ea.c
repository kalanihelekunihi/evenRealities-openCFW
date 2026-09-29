
undefined8 FUN_005e50ea(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  iVar2 = td_state_ptr_alias1();
  iVar3 = td_session_struct_ptr();
  if (param_1 == '\0') {
    uVar4 = 2;
  }
  else {
    cVar1 = *(char *)(iVar2 + 0xa1d8);
    if (cVar1 == '\x01') {
      uVar4 = 4;
    }
    else if (cVar1 == '\0') {
      uVar4 = 3;
    }
    else if (cVar1 == '\x02') {
      if ((iVar3 == 0) || (*(short *)(iVar3 + 0x406) == 0)) {
        iVar2 = FUN_005e505a();
        if (iVar2 == 0) {
          cVar1 = td_record_status_read();
          if ((cVar1 == '\x01') || (cVar1 == '\x02')) {
            uVar4 = 6;
          }
          else {
            uVar4 = 5;
          }
        }
        else {
          *(int *)(DAT_005e53b4 + 0x288) = iVar2;
          uVar4 = 0x16;
        }
      }
      else {
        uVar4 = 7;
      }
    }
    else {
      uVar4 = 3;
    }
  }
  return CONCAT44(param_4,uVar4);
}

