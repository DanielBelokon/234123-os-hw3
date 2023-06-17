#include "queue.h"

Queue queueCreate()
{
    Queue queue = malloc(sizeof(struct queue));
    if (pthread_mutex_init(&queue->mutex, NULL) != 0)
    {
        printf("mutex init failed\n");
        return 1;
    }

    if (pthread_cond_init(&queue->cond, NULL) != 0)
    {
        printf("cond init failed\n");
        return 1;
    }

    queue->size = 0;
    queue->head = NULL;
    queue->tail = NULL;
    return queue;
}

void queueDestroy(Queue queue)
{
    while (queue->size > 0)
    {
        queueRemove(queue);
    }
    free(queue);
}

void queueInsert(Queue queue, int connfd)
{
    pthread_mutex_lock(&queue->mutex);
    Node node = malloc(sizeof(struct node));
    node->connfd = connfd;
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
    pthread_cond_signal(&queue->cond);
    pthread_mutex_unlock(&queue->mutex);
}

int queueRemove(Queue queue)
{
    pthread_mutex_lock(&queue->mutex);
    while (queueIsEmpty(queue))
    {
        pthread_cond_wait(&queue->cond, &queue->mutex);
    }

    if (queue->size == 0)
    {
        return -1;
    }
    Node node = queue->head;
    queue->head = node->next;
    int connfd = node->connfd;
    free(node);
    queue->size--;
    pthread_mutex_unlock(&queue->mutex);
    return connfd;
}

int queueIsEmpty(Queue queue)
{
    return queue->size == 0;
}

int queueSize(Queue queue)
{
    return queue->size;
}
