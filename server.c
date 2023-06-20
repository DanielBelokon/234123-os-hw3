#include "segel.h"
#include "request.h"
#include "queue.h"
#include "schedpolicy.h"

// 
// server.c: A very, very simple web server
//
// To run:
//  ./server <portnum (above 2000)>
//
// Repeatedly handles HTTP requests sent to this port number.
// Most of the work is done within routines written in request.c
//

typedef struct server_args_t
{
    int port;
    int threads;
    int queue_size;
    void (*schedalg)(int connfd, struct timeval arrival_time, Queue queue, int max_size);
    int max_size;
} server_args;

Queue queue;

// HW3: Parse the new arguments too
void getargs(server_args *sa, int argc, char *argv[])
{
    if (argc < 4)
    {
        sa->port = 9999;
        sa->threads = 4;
        sa->queue_size = 20;
        sa->schedalg = &sched_block;
        sa->max_size = 20;
        return;
        fprintf(stderr, "Usage: %s <port> <threads> <queue_size> <schedalg> [<max_size>]\n", argv[0]);
        exit(1);
    }
    sa->port = atoi(argv[1]);
    sa->threads = atoi(argv[2]);
    sa->queue_size = atoi(argv[3]);
    sa->schedalg = decidePolicy(argv[4]);

    if (argc > 5)
        sa->max_size = atoi(argv[5]);
    else
        sa->max_size = sa->queue_size;
}
// "block", "dt", "dh", "bf", "dynamic", or "random"

void thread(int thread_num)
{
    pthread_detach(pthread_self());
    thread_statistics threadstats = malloc(sizeof(struct thread_statistics_t));
    threadstats->handler_thread_id = thread_num;
    threadstats->request_count = 0;
    threadstats->static_requests_count = 0;
    threadstats->dynamic_requests_count = 0;

    while (1)
    {
        struct timeval arrival_time;
        int connfd = queueRemove(queue, &arrival_time);
        increment_in_progress();
        // TODO change to getT
        gettimeofday(&threadstats->dispatch_interval, NULL);

        timersub(&threadstats->dispatch_interval, &arrival_time, &threadstats->dispatch_interval);
        threadstats->arrival_time = arrival_time;
        requestHandle(connfd, threadstats);
        Close(connfd);
        decrement_in_progress();
    }
}

int main(int argc, char *argv[])
{
    int listenfd, connfd, clientlen;
    server_args sa;

    struct sockaddr_in clientaddr;
    pthread_t tid;

    // setup fd queue

    getargs(&sa, argc, argv);
    queue = queueCreate(sa.queue_size);

    for (size_t i = 0; i < sa.threads; i++)
    {
        pthread_create(&tid, NULL, thread, i);
        pthread_detach(tid);
    }

    listenfd = Open_listenfd(sa.port);
    while (1) {
        clientlen = sizeof(clientaddr);
        connfd = Accept(listenfd, (SA *)&clientaddr, (socklen_t *)&clientlen);
        struct timeval arrival_time;
        gettimeofday(&arrival_time, NULL);
        sa.schedalg(connfd, arrival_time, queue, sa.max_size);
    }

}


    


 
