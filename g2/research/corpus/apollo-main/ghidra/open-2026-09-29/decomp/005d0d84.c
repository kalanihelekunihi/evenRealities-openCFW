
undefined1 FUN_005d0d84(undefined4 *param_1,char *param_2)

{
  undefined1 uVar1;
  char *pcVar2;
  
  pcVar2 = (char *)*param_1;
  uVar1 = 0;
  if ((((pcVar2 + 3 < param_2) && (*pcVar2 == 't')) && (pcVar2[1] == 'r')) &&
     ((pcVar2[2] == 'u' && (pcVar2[3] == 'e')))) {
    uVar1 = 1;
    pcVar2 = pcVar2 + 5;
  }
  else if ((((pcVar2 + 4 < param_2) && ((*pcVar2 == 'f' && (pcVar2[1] == 'a')))) &&
           (pcVar2[2] == 'l')) && ((pcVar2[3] == 's' && (pcVar2[4] == 'e')))) {
    uVar1 = 0;
    pcVar2 = pcVar2 + 6;
  }
  *param_1 = pcVar2;
  return uVar1;
}

