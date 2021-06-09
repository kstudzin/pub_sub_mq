# cs6381-assignment1: Single Broker Publish-Subscribe

## Introduction
Multiple patterns have been established to facilitate message delivery within applications. This Application Programming Interface (API) provides and way to utilize the relatively simple Publisher/Subscriber model. This API allows a developer two options for how message passing would occur within their application. One provides an intermediary through which all messages pass from a publisher to a subscriber. The other option provides a means of discovery such that a subscriber can find publishers to receive messages from directly.

### What
There are three entities at the core of this API: publishers, subscribers, and brokers. Publishers are entities that publishes messages and an associated topic. Subscribers are entities that subscribe to receive messages on topics. Brokers are entities that facilitate connecting publishers and subscribers. The different broker implementations determine which message passing mechanism of the two discussed above is used in the implementation. The broker that serves as the intermediary is called the routing broker, and the broker that helps subscribers find publishers to connect to is called the direct broker.

### Why
Given the popularity of communication within applications, message passing is one step shy of required for modern applications. Providing this service to users helps to increase engagement of the user base without adding any additional work for content developers. Once the messaging service is incorporated into the application, the users become a significant source of interactive content.

### When
Publish/Subscribe is an appropriate message passing choice when the publishers and subscribers may come and go because neither the publishers nor the subscribers depend on the other existing. In other words, a publisher may have no subscribers in which case messages are dropped, and a subscriber can register for a topic on which no publishers are currently publishing in which case it does not receive messages. 

## How (it works)

### Broker
The goal of the broker is to decouple publishers and subscribers so that they do not need to know the address of the entities that they want to connect to. To accomplish this, the broker has an address that is well-known to publishers and subscribers. The broker must be running as a service on that address, and then applications can create publishers and subscribers that connect to the well-known address to register what topics they would like to send and receive messages on.

As discussed in the introduction, there are two broker configurations. The user must select either routing or direct broker configuration when starting the service. The broker configuration determines the registration protocol as well as the connections that are made to send messages. In the routing configuration all parties register with the broker serves as an intermediary. After registration, when publishers send messages, they are received by the broker which forwards them to the subscribers.

The broker maintains three connections to manage these processes. One connection is bound to the brokers address - this is used for registration. One connection connects to all the publishers' addresses - this is used for receiving messages. The publishers' addresses are bound to the other side of the connection. During registration, this connection subscribes to the topic that the publisher is registering for. The third connection connects to all the subscribers addresses - this is used to send messages to the subscribers. The subscribers' addresses are bound to the other side of the connection and manages the topics it is subscribing to.

Two processes run concurrently in this configuration. One process waits for the registration connection to receive messages; this is done in the `process_registration` method. Another process waits for the message receiving connection; this is done in the `process` method. Both of these methods need to be called in loops in separate threads to run this configuration as a service. 

The other configuration, known as the direct broker, serves as a mechanism to facilitate a direct connection between publishers and subscribers. Similarly to the routing configuration, both publishers and subscribers must register with the broker before publishing; however the registering is more complex in this configuration. Here, the broker has two connections: an initial registration connection bound to the broker's address and a connection, also used in the registration process, that connects to the subscribers' addresses such that the broker can inform subscribers of new publishers they should connect to. This is a complex process, so let's dive in a little deeper.

When a publisher registers, it sends its address and a topic to the connection bound to the broker's address. When the broker receives this message, it first adds the topic and address to a record of the addresses publishing on each topic which will be used later when a subscriber registers. Then it publishes a message to all registered subscribers on the second connection mentioned in the prior paragraph. The message's topic is the topic that the publisher is registering for and the body of the message is the publisher's address. We will discuss how the subscriber uses this information in the subscriber section.

When a subscriber registers, it also sends its  address and a topic to the connection bound to the broker's address. When the broker receives this message, it responds by sending the subscriber a list of publishers' addresses publishing on the topic the subscriber registered for. It is the subscriber's responsibility to connect to these addresses. 

After that registration process the broker will not communicate with the publisher until the publisher registers additional topics. The subscribers register with this broker type only for the purpose of discovering if there are publishers for a given topic. If publishers exist for a topic the subscriber will receive a list of addresses from the broker that they can connect to. If a publisher registers for a topic after a subscriber has subscribed then a message will be sent to subscribers with the location of the new publisher.

### Publisher

The behavior of the publisher does not change based upon the configuration of the broker. The publisher will establish a connection to the well known broker and registers the topic(s) that it will be publishing as well as its own address with the broker. Once the handshake has occured with the broker, the publisher may begin publishing messages without any regard for what entities may or may not be listening for those messages. Users of the API should note that existing registered subscribers may miss messages if a publisher registers for a topic and immediately begins sending messages because it takes more time to make the connection than to send the messages.

### Subscriber

The behavior of the subscriber varies based upon the broker configuration. In both configurations, the subscriber establishes a connection with the well known broker and a connection to receive messages on. The first connection allows the subscriber to register interest in topics by connecting to the broker address. The second connection binds to the subscriber's address in the routing configuration and connects to the publishers' addresses in the direct configuration. 
'
To register with the routing broker, the subscriber informs the broker of the address at which it will be listening for all topics sent from the broker. The broker will connect to that address so that it receives the messages the broker forwards from the publishers.

To register with the direct broker, the subscriber inform the broker of its address at which it will be listening for new publisher registrations. The broker connects to that address and then sends the subscriber the addresses of the publishers for the given topic.  Upon receipt, subscriber establishes connections directly with each of publishers that it has subscribed. 

In each case, the subscriber will also set the topics to receive messages for on the message receiving connection so that the underlying connection can ensure it only receives messages it is interested in. The message receiving connection waits to receive messages in the `wait_for_msg` method on the subscriber. For a subscriber to receive connections this method must be run in a thread in a loop. 

When using a direct publisher, the subscriber also maintains a third connection that subscribes to updates from the broker on new publishers that are registering. When used, this connection is bound to the subscriber's address. This connection waits for messages in the `wait_for_registration` method which must be run in a loop in a thread.

### Diagrams

[Routing Broker Diagram](https://user-images.githubusercontent.com/76195473/121063916-ea9a4c80-c794-11eb-9a7f-162a83d3ed62.png)

  * All message passing goes through routing broker.

[Direct Broker Diagram](https://user-images.githubusercontent.com/76195473/121063991-07cf1b00-c795-11eb-910e-6cae570af6cb.png)

  * Both publishers and subscribers register with the broker but messages are sent directly.

## How (to use)

### API

#### Required
 * Python 3
 * [Install 0mq](https://zeromq.org/download/)

#### Publisher

Contruct an instance of a publisher with its own address and the brokers address:
```
Publisher(address = <address of this publisher>, registration_address = <address of the broker>)
```

Register the publisher with the broker for the given topic:

```
register(topic = <string>)
```

Publishe a message for a given topic in one of three message formats:

```
publish(topic = <string>, message = <string>, message_type = <default = MessageType.STRING>)
MessageType = [STRING, PYOBJ, JSON]
```

#### Subscriber

Construct an instance of a subscriber with its own address and the brokers address:

```
Subscriber(address = <address of this subscriber>, registration_address = <address of the broker>)
```

Register the subscriber with the broker for the given topic:

```
register(topic = <string>)
```

Unregister the subscriber with the broker for the given topic. Subscriber will stop receiving messages on the topic:
  
```
unregister(topic = <string>)
```

Register a callback that accepts a topic and message to notify the application that the subscriber has received a message:

```
register_callback(callback = Function or method to be called when a message is received)
```

Wait to receive messages:

* Once subscriber has registered, application must be running wait_for_msg() in a loop 
* Upon receipt of a message the application is notified via the registered callback

```
wait_for_msg()
```

Receive notifications of publisher registration from broker:

* Only used with direct broker
* Must be running in a loop in a thread 

```
wait_for_registration()
```

#### Brokers

**RoutingBroker**

Construct an instance of routing broker at its well known address:

```
RoutingBroker(address = <address of broker>)
```

Wait to receive registrations from publishers or subscribers:

* Must be running in a loop in a thread

```
process_registration()
```


Waits to receive messages from publishers:

* Must be running in a loop in a thread
```
process()
```

**DirectBroker**

Construct an instance of routing broker at its well known address:

```
DirectBroker(address = <address of broker>)
```

Wait to receive registrations from publishers or subscribers:

* Must be running in a loop in a thread

```
process_registration()
```

#### Unit Testing

Run unit tests:

`$ pytest`

Run tests and get coverage report

`$ pytest --cov=pubsub -cov-report html`

### CLI

This CLI is an application using the publish/subscriber API described above.

#### Required packages
 * [Install Faker](https://faker.readthedocs.io/en/master/#basic-usage)

**Start broker**

To see full help menu: `python psserver.py -h`

Example: `python psserver.py --type r --address 127.0.0.1 --port 5555`

**Start subscriber**

To see full help menu: `python ps_subscriber.py -h`

Example: `python ps_subscriber.py tcp://127.0.0.1:5557 tcp://127.0.0.1:5555 --t hello`

**Start publisher**

To see full help menu: `python ps_publisher.py -h`

Example: `python ps_publisher.py tcp://127.0.0.1:5556 tcp://127.0.0.1:5555 --t hello --r 100 --d 1.5`

### Performance Testing

#### Recommended
 * [Install Virtual Machine](https://www.virtualbox.org/wiki/Downloads)
 * [Install Ubuntu OS on VM](https://linuxconfig.org/how-to-install-ubuntu-20-04-on-virtualbox)
 * [Install Mininet](http://mininet.org/download/)
 * Install xterm on OS: Ubuntu `sudo apt-get install -y xterm`

#### Mininet
 * Open terminal in virtual machine operating system
 * Start mininet service `sudo mn --topo single, 3` switch = single , hosts = 3
 * Start multiple terminals `xterm h1 h2 h3`
 * Start one of each CLIs listed below within each of the terminal windows

#### Automated Testing
 * Open terminal in virtual machine operating system
 * Run `sudo python single_switch.py <number of subscribers>`

### File Descriptions

* *FOLDER* - cs6381-assignment1
  * *FOLDER* - latency
    * automated testing result files (sub-#_broker-#.log, test.png)
  * *FOLDER* - pubsub
    * \_\_init\_\_.py - Package initializer with dual log file creation 1 for application information and 1 for performance analysis
    * broker.py - Three classes for API an AbstractBroker, RoutingBroker(AbstractBroker), and DirectBroker(AbstractBroker)
    * publisher.py - One class that creates well known connection for message passing regardless of broker type
    * subscriber.py - One class that either connects to RoutingBroker or connects to multiple Subscribers based upon addresses provided by DirectBroker
    * util.py - internal API helper file
  * *FOLDER* - tests
    * *FOLDER* - integration
      * test_pubsub.py - integration tests
    * test_direct_broker.py - units tests
    * test_publisher.py - units tests
    * test_routing_broker.py - units tests
    * test_subscriber.py - units tests
  * latency_analysis.py - Utility for reading csv file into graphing function which is then output to test.png
  * ps_publisher.py - CLI to register for a topic and publish messages
  * ps_subscriber.py - CLI to register for a topic and receive messages
  * psserver.py - CLI to start direct or routing broker
  * single_switch.py - automated latency testing

#### PERFORMANCE TESTING: LATENCY ANALYSIS

**Statistics**
```
             001_d        001_r        002_d        002_r        004_d        004_r        008_d        008_r         016_d         016_r
count  1000.000000  1000.000000  2000.000000  2000.000000  4000.000000  4000.000000  8000.000000  8000.000000  16000.000000  16000.000000
mean      0.084348     0.037717     0.087789     0.097000     0.142497     0.146839     0.283256     0.334443      0.606059      0.611125
std       0.056347     0.037808     0.069261     0.074146     0.127648     0.117144     0.263280     0.291161      0.569671      0.561630
min       0.000105     0.000842     0.000067     0.000203     0.000086     0.000742     0.000142     0.000380      0.000130      0.001209
25%       0.003239     0.005228     0.000236     0.000739     0.000292     0.015125     0.019072     0.038494      0.012043      0.028659
50%       0.118551     0.029139     0.086006     0.106523     0.151019     0.154681     0.247727     0.283521      0.504681      0.497885
75%       0.125188     0.058104     0.160943     0.168650     0.241981     0.253651     0.530503     0.599421      1.118283      1.065992
max       0.131203     0.164185     0.180269     0.209540     0.369497     0.346041     0.776108     0.918261      1.724125      1.800703
```

**Mode**

```
       001_d     001_r     002_d     002_r     004_d     004_r     008_d     008_r     016_d     016_r
0   0.000114  0.001315  0.000114  0.000273  0.000144  0.004843  0.005141  0.038494  0.000235  0.019645
1   0.000119  0.001617       NaN  0.000304       NaN  0.006383  0.167435       NaN  0.000283  0.020640
2   0.000140  0.094738       NaN  0.000323       NaN  0.006420       NaN       NaN  0.000308  0.021603
3   0.000149       NaN       NaN  0.000328       NaN  0.006520       NaN       NaN  0.000979       NaN
4   0.000183       NaN       NaN  0.000330       NaN  0.006744       NaN       NaN  0.004291       NaN
5   0.000193       NaN       NaN  0.000370       NaN  0.007340       NaN       NaN  0.005635       NaN
6   0.000320       NaN       NaN  0.000424       NaN  0.007867       NaN       NaN  0.010745       NaN
7   0.003371       NaN       NaN       NaN       NaN  0.008100       NaN       NaN       NaN       NaN
8   0.124150       NaN       NaN       NaN       NaN  0.008106       NaN       NaN       NaN       NaN
9   0.124246       NaN       NaN       NaN       NaN  0.008520       NaN       NaN       NaN       NaN
10  0.130786       NaN       NaN       NaN       NaN  0.008808       NaN       NaN       NaN       NaN
```

**Plotted Graphs**

