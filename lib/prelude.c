#include <stdlib.h>
#include <stdio.h>
#include <string.h>


struct S {
    char* text;
    unsigned int cnt;
};


struct S* __builtin__add_string(struct S* a, struct S* b)
{
    int la = strlen(a->text);
    int lb = strlen(b->text);
    char* caption = malloc(sizeof(char)*(la+lb+1));
    struct S* ret = malloc(sizeof(struct S));
    strcpy(caption, a->text);
    strcpy(caption+la, b->text);
    ret->cnt = 1;
    ret->text = caption;
    // printf("creating %p: %p %d\n", ret, ret->text, ret->cnt);
    return ret;
}


int __builtin__eq_string(struct S* a, struct S* b)
{
    return strcmp(a->text, b->text) == 0;
}


int __builtin__ne_string(struct S* a, struct S* b)
{
    return strcmp(a->text, b->text) != 0;
}


void __builtin__delref_string(struct S* a)
{
    // printf("deleting at %p:\n", a);
    a->cnt--;
    if (a->cnt == 0)
    {
        // printf("deleting %p\n", a);
        free(a->text);
        free(a);
    }
    // else
    //     printf("left %d\n", a->cnt);
}


void __builtin__addref_string(struct S* a)
{
    a->cnt++;
}

void printInt(int x)
{
    printf("%d\n", x);
}

int readInt()
{
    int x;
    scanf("%d\n", &x);
    return x;
}

void printString(struct S* a)
{
    puts(a->text);
}


struct S* readString()
{
    char* caption = malloc(sizeof(char)*1000);
    scanf("%[^\n]\n", caption);
    struct S* ret = malloc(sizeof(struct S));
    ret->cnt = 1;
    ret->text = caption;
    return ret;
}

void error()
{
    printf("runtime error\n");
    exit(-1);
}


struct S foo = {"alamakota", 1000000000};
