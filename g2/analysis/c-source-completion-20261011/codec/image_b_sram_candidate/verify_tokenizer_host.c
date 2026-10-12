#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
extern char *gx8002_image_b_tokenize_100112d4(char *, const char *);
char *gx8002_image_b_token_cursor_2002d3e0;
int main(void){
 char **saved=&gx8002_image_b_token_cursor_2002d3e0; *saved=NULL;
 char s[]="::alpha,beta::gamma";
 assert(strcmp(gx8002_image_b_tokenize_100112d4(s,":,"),"alpha")==0);
 assert(strcmp(gx8002_image_b_tokenize_100112d4(NULL,":,"),"beta")==0);
 assert(strcmp(gx8002_image_b_tokenize_100112d4(NULL,":,"),"gamma")==0);
 assert(gx8002_image_b_tokenize_100112d4(NULL,":,")==NULL);
 assert(*saved==NULL);
 char e[]=":::";assert(gx8002_image_b_tokenize_100112d4(e,":")==NULL);
 char n[]="ab";assert(strcmp(gx8002_image_b_tokenize_100112d4(n,""),"ab")==0);
 assert(gx8002_image_b_tokenize_100112d4(NULL,"")==NULL);
 puts("7/7 tokenizer cursor and separator fixtures");
}
