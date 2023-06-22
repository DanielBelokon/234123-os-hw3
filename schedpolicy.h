#ifndef _SCHEDPOLICY_H_
#define _SCHEDPOLICY_H_

#include "queue.h"

int in_progress = 0;

pthread_mutex_t in_progress_mutex = PTHREAD_MUTEX_INITIALIZER;

void increment_in_progress()
{
    pthread_mutex_lock(&in_progress_mutex);
    in_progress++;
    pthread_mutex_unlock(&in_progress_mutex);
}

void decrement_in_progress()
{
    pthread_mutex_lock(&in_progress_mutex);
    in_progress--;
    pthread_mutex_unlock(&in_progress_mutex);
}

int get_in_progress()
{
    pthread_mutex_lock(&in_progress_mutex);
    int ret = in_progress;
    pthread_mutex_unlock(&in_progress_mutex);
    return ret;
}

void sched_block(int connfd, struct timeval arrival_time, Queue queue, int max_size)
{
    // Queue already has cond and mutex to handle this
    queueInsert(queue, connfd, arrival_time);
}

void sched_dt(int connfd, struct timeval arrival_time, Queue queue, int max_size)
{
    if (queueGetSize(queue) + get_in_progress() >= queueGetCapacity(queue))
    {
        Close(connfd);
        return;
    }
    else
    {
        queueInsert(queue, connfd, arrival_time);
    }
}

void sched_dh(int connfd, struct timeval arrival_time, Queue queue, int max_size)
{
    if (queueGetSize(queue) + get_in_progress() >= queueGetCapacity(queue))
    {
        struct timeval temp;
        Close(queueRemove(queue, &temp, 0));
    }

    queueInsert(queue, connfd, arrival_time);
}

void sched_bf(int connfd, struct timeval arrival_time, Queue queue, int max_size)
{
    if (queueGetSize(queue) + get_in_progress() >= queueGetCapacity(queue))
    {
        queueWaitEmpty(queue);
    }

    queueInsert(queue, connfd, arrival_time);
}

void sched_dynamic(int connfd, struct timeval arrival_time, Queue queue, int max_size)
{
    if (queueGetSize(queue) + get_in_progress() >= queueGetCapacity(queue))
    {
        Close(connfd);
        if (max_size > queueGetCapacity(queue))
            queueIncrementCapacity(queue);
    }
    else
    {
        queueInsert(queue, connfd, arrival_time);
    }
}

void sched_random(int connfd, struct timeval arrival_time, Queue queue, int max_size)
{
    // remove 50% of the queue if it's full in random order
    pthread_mutex_lock(&queue->mutex);
    if (queue->size + get_in_progress() >= queue->capacity)
    {
        int count = queue->size;
        for (int i = 0; i < count / 2; i++)
        {
            Node node = queue->head;
            queue->head = node->next;
            Close(node->connfd);
            free(node);
            queue->size--;
        }

        pthread_cond_signal(&queue->cond_not_full);
    }
    pthread_mutex_unlock(&queue->mutex);
    queueInsert(queue, connfd, arrival_time);
}

void *decidePolicy(const char *policy)
{

    if (strcmp(policy, "block") == 0)
    {
        return sched_block;
    }
    else if (strcmp(policy, "dt") == 0)
    {
        return sched_dt;
    }
    else if (strcmp(policy, "dh") == 0)
    {
        return sched_dh;
    }
    else if (strcmp(policy, "bf") == 0)
    {
        return sched_bf;
    }
    else if (strcmp(policy, "dynamic") == 0)
    {
        return sched_dynamic;
    }
    else if (strcmp(policy, "random") == 0)
    {
        return sched_random;
    }
    else /* default: */
    {
        return sched_dt;
    }
}

#endif // _SCHEDPOLICY_H_