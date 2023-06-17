#ifndef Queue_h
#define Queue_h

#include "segel.h"
#include <stdlib.h>
#include <pthread.h>

typedef struct node
{
    int connfd;
    struct node *next;
} *Node;

typedef struct queue
{
    int size;
    Node head;
    Node tail;

    pthread_mutex_t mutex;
    pthread_cond_t cond;
} *Queue;

Queue queueCreate();
void queueDestroy(Queue queue);
void queueInsert(Queue queue, int connfd);
int queueRemove(Queue queue);
int queueIsEmpty(Queue queue);
int queueSize(Queue queue);

#endif