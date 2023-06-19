#include "queue.h"

Queue queueCreate(int q_capacity)
{
    Queue queue = malloc(sizeof(struct queue));
    if (pthread_mutex_init(&queue->mutex, NULL) != 0)
    {
        printf("mutex init failed\n");
        return 1;
    }

    if (pthread_cond_init(&queue->cond_not_empty, NULL) != 0)
    {
        printf("cond init failed\n");
        return 1;
    }

    if (pthread_cond_init(&queue->cond_not_full, NULL) != 0)
    {
        printf("cond init failed\n");
        return 1;
    }

    queue->size = 0;
    queue->capacity = q_capacity;
    queue->head = NULL;
    queue->tail = NULL;
    return queue;
}

void queueDestroy(Queue queue)
{
    time_t temp;
    while (queue->size > 0)
    {
        queueRemove(queue, &temp);
    }
    free(queue);
}

void queueInsert(Queue queue, int connfd, struct timeval arrival_time)
{
    pthread_mutex_lock(&queue->mutex);
    while (queue->size == queue->capacity)
    {
        pthread_cond_wait(&queue->cond_not_full, &queue->mutex);
    }

    Node node = malloc(sizeof(struct node));
    node->connfd = connfd;
    node->arrival_time = arrival_time;
    node->next = NULL;
    if (queue->size == 0)
    {
        queue->head = node;
        queue->tail = node;
    }
    else
    {
        queue->tail->next = node;
        queue->tail = node;
    }
    queue->size++;
    pthread_cond_signal(&queue->cond_not_empty);
    pthread_mutex_unlock(&queue->mutex);
}

int queueRemove(Queue queue, struct timeval *arrival_time)
{
    pthread_mutex_lock(&queue->mutex);
    while (queueIsEmpty(queue))
    {
        pthread_cond_wait(&queue->cond_not_empty, &queue->mutex);
    }

    if (queue->size == 0)
    {
        return -1;
    }
    Node node = queue->head;
    queue->head = node->next;
    int connfd = node->connfd;
    *arrival_time = node->arrival_time;
    free(node);
    queue->size--;

    pthread_cond_signal(&queue->cond_not_full);

    if (queue->size == 0)
    {
        pthread_cond_signal(&queue->cond_empty);
    }

    pthread_mutex_unlock(&queue->mutex);
    return connfd;
}
int queueGetSize(Queue queue)
{
    pthread_mutex_lock(&queue->mutex);
    int curSize = queue->size;
    pthread_mutex_unlock(&queue->mutex);
    return curSize;
}

int queueGetCapacity(Queue queue)
{
    pthread_mutex_lock(&queue->mutex);
    int curCapacity = queue->capacity;
    pthread_mutex_unlock(&queue->mutex);
    return curCapacity;
}

void queueSetCapacity(Queue queue, int newCapacity)
{
    pthread_mutex_lock(&queue->mutex);
    queue->capacity = newCapacity;
    pthread_mutex_unlock(&queue->mutex);
}

void queueIncrementCapacity(Queue queue)
{
    pthread_mutex_lock(&queue->mutex);
    queue->capacity++;
    pthread_mutex_unlock(&queue->mutex);
}

int queueIsEmpty(Queue queue)
{
    return queue->size == 0;
}

int queueSize(Queue queue)
{
    return queue->size;
}

void queueWaitEmpty(Queue queue)
{
    pthread_mutex_lock(&queue->mutex);
    while (queue->size != 0)
    {
        pthread_cond_wait(&queue->cond_empty, &queue->mutex);
    }
    pthread_mutex_unlock(&queue->mutex);
}
