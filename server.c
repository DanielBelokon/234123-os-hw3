#include "segel.h"
#include "request.h"
#include "queue.h"

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
    int schedalg;
    int max_size;
} server_args;

Queue queue;

// HW3: Parse the new arguments too
void getargs(server_args *sa, int argc, char *argv[])
{
    if (argc < 4)
    {
        fprintf(stderr, "Usage: %s <port>\n", argv[0]);
        exit(1);
    }
    sa->port = atoi(argv[1]);
    sa->threads = atoi(argv[2]);
    sa->queue_size = atoi(argv[3]);
    // sa->schedalg = atoi(argv[4]);
    // sa->max_size = atoi(argv[5]);
}

void thread()
{
    pthread_detach(pthread_self());
    while (1)
    {
        int connfd = queueRemove(queue);
        requestHandle(connfd);
        Close(connfd);
    }
}

int main(int argc, char *argv[])
{
    int listenfd, connfd, clientlen;
    server_args sa;

    struct sockaddr_in clientaddr;
    pthread_t tid;

    // setup fd queue
    queue = queueCreate();

    getargs(&sa, argc, argv);

    for (size_t i = 0; i < sa.threads; i++)
    {
        pthread_create(&tid, NULL, thread, NULL);
        pthread_detach(tid);
    }

    //
    // HW3: Create some threads...

    listenfd = Open_listenfd(sa.port);
    while (1) {
        clientlen = sizeof(clientaddr);
        connfd = Accept(listenfd, (SA *)&clientaddr, (socklen_t *)&clientlen);
        queueInsert(queue, connfd);
    }

}


    


 
