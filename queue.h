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
    int capacity;
    Node head;
    Node tail;

    pthread_mutex_t mutex;
    pthread_cond_t cond_not_empty;
    pthread_cond_t cond_not_full;

    pthread_cond_t cond_empty;
} *Queue;

Queue queueCreate();
void queueDestroy(Queue queue);
void queueInsert(Queue queue, int connfd);
int queueRemove(Queue queue);
int queueIsEmpty(Queue queue);
int queueSize(Queue queue);
int queueGetCapacity(Queue queue);
void queueSetCapacity(Queue queue, int capacity);
void queueIncrementCapacity(Queue queue);
void queueWaitEmpty(Queue queue);

#endif