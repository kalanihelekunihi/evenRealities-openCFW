
byte FUN_005890f6(char *param_1,char param_2,char param_3)

{
  byte bVar1;
  byte bVar2;
  
  if ((*param_1 == '\x04') && (param_1[1] == '\x04')) {
    bVar2 = 0;
  }
  else if ((*param_1 == param_2) && (param_1[1] == param_3)) {
    bVar2 = 1;
  }
  else {
    if ((*param_1 == param_2) || (*param_1 == '\x04')) {
      bVar2 = 1;
    }
    else {
      bVar2 = 0;
    }
    if ((param_1[1] == param_3) || (param_1[1] == '\x04')) {
      bVar1 = 1;
    }
    else {
      bVar1 = 0;
    }
    bVar2 = bVar2 & bVar1;
  }
  return bVar2;
}

