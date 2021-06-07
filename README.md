# cs6381-assignment1: Single Broker Publish-Subscribe

### Narrative

#### Who
There are multiple patterns that have been established to facilitate message delivery within applications. This Application Programming Interface(API) provides and way to utilize the relatively simple Publisher/Subscriber model. This API allows a developer two options for how message passing would occur within their application. One provides an intermediary through which all messages pass from a publisher to a subscriber. The second option simply provides a means of discovery such that a subscriber can find a publisher to receive messages from directly.

#### What
[See File Descriptions below](#file-descriptions)


#### When
Given the popularity of digital communication with applications, message passing is one step shy of required for modern applications. Providing this service to users helps to increase engagement of the user base without adding any additional work for content developers. Once the messaging service is incorporated into the application the users become a significant source of interactive content.

#### Why
This API minimizes the development time to integrate message passing into an application by providing a few simple options at each link in the messaging chain. Additonally, this API decouples publishers from subscribers, meaning that a publisher may have no subscribers and a subscriber can register for a topic regardless of whether a publisher existing for said topic. At the server level the application has the choice to handle all messages or merely serve as a registration mechanism. The publishers have but two options they can **register** for a topic or **publish** a message on that topic. The subscribers can choose to **subscribe** or **unsubscribe** from a topic, as well as, **listen** to all topics for which they have registered.

#### How (it works)
- [ ] TODO Review
##### Broker
The broker in this messaging API incorporates space decoupling among publishers and subscribers. This means that either party can exist regardless of the presence of the opposing party. When you first start the server you have two options regarding the work that will be required by this entity. 
You can choose the routing option to have all parties register with the broker that handles the work of serving as an intermediary for all messages passing from publishers to subscribers. The broker also in continues listening for parties registering. 
The second option, known as the direct broker, only serves as a mechanism for publishers to register who they are(location) and which topic(s) that they will be publishing. After that registration process the broker will not communicate with the publisher again unless the publisher registers additional topics. The subscribers register with this broker type only for the purpose of discovering if there are publisher(s) for a given topic. If publishers exist for a topic the subscriber will receive a list of addresses from the broker that they can connect to. If a publisher registers for a topic after a subscriber has subscribed then a message will be sent to subscribers with the location of the new publisher.

##### Publisher
The behavior of the publisher does not change based upon the configuration of the broker. The publisher will establish a connection to the well known broker and registers with the broker the topic(s) that it will be publishing as well as its own location. Once the handshake has occured with the broker, the publisher may begin publishing messages without any regard for what entities may or may not be "listening" for those messages. There exists an edge case where subscribers may miss messages if a publisher registers for a topic and immediately begins sending messages.

##### Subscriber
The behavior of the subscriber varies only slighly based upon the configuration of the broker, not so much as to how, but who. In both scenarios the subscriber establishes a connection with the well known broker. This connection allows for the subscriber to register interest in one or more topics at any time. The second connection that is established by the subscriber does depend upon the broker type. 
In the case of the routing broker, the subscriber will inform the broker of its well known location at which it will be listening for all topics sent from the broker. From that point all messages from all publishers for a given topic will be passed to the subscriber.
In the direct broker scenario, the address of the publisher is received by the subscriber upon registration for a given topic.  Upon receipt, subscriber establishes connections directly with each of publishers that they have subscribed. 

#### How (to use)
[See Command Line Interface(CLI) Usage below](#command-line-interface-usage)

[See Application Programming Interface(API) Usage below](#application-programming-interfaceapi)

<hr>

### BROKER PROCESS DIAGRAMS

[Routing_Broker_Diagram](https://user-images.githubusercontent.com/76195473/121063916-ea9a4c80-c794-11eb-9a7f-162a83d3ed62.png)

  * All message passing goes through routing broker.

[Direct_Broker_Diagram](https://user-images.githubusercontent.com/76195473/121063991-07cf1b00-c795-11eb-910e-6cae570af6cb.png)

  * Direct broker holds registry to all publishers to send messages directly to subscribers who register for topics.

<hr>

### FILE DESCRIPTIONS
- [ ] TODO Revise base on pending merges 06/07/2021
* *FOLDER* - cs6381-assignment1
  * *FOLDER* - pubsub
    * \_\_init\_\_.py - Package initializer with dual log file creation 1 for application information and 1 for performance analysis
    * broker.py - Three classes for API an AbstractBroker, RoutingBroker(AbstractBroker), and DirectBroker(AbstractBroker)
    * publisher.py - One class that creates well known connection for message passing regardless of broker type
    * subscriber.py - One class that either connects to RoutingBroker or connects to multiple Subscribers based upon addresses provided by DirectBroker
    * util.py - internal API helper file
  * *FOLDER* - tests
    * test_direct_broker.py - units tests
    * test_publisher.py - units tests
    * test_routing_broker.py - units tests
    * test_subscriber.py - units tests
  * psserver.py - CLI to start direct or routing broker
  * ps_publisher.py - CLI to register for a topic and publish messages
  * ps_subscriber.py - CLI to register for a topic and receive messages

<hr>

### SYSTEM DEMONSTRATION
#### RECOMMENDED
 * [Install Virtual Machine](https://www.virtualbox.org/wiki/Downloads)
 * [Install Ubuntu OS on VM](https://linuxconfig.org/how-to-install-ubuntu-20-04-on-virtualbox)

#### REQUIRED
 * [Install 0mq](https://zeromq.org/download/)
 * [Install Faker](https://faker.readthedocs.io/en/master/#basic-usage)
 * [Install Mininet](http://mininet.org/download/)
 * Install xterm on OS: Ubuntu `sudo apt-get install -y xterm`

#### MININET
 * Open terminal in virtual machine operating system
 * Start mininet service `sudo mn --topo single, 3` switch = single , hosts = 3
 * Start multiple terminals `xterm h1 h2 h3`
 * Start one of each CLIs listed below within each of the terminal windows
<hr>

### COMMAND LINE INTERFACE USAGE
- [ ] TODO Review base on pending merges 06/07/2021
* psserver.py - start broker
  * -h : Help - to see argument options
  * Example: python3 psserver.py --t r --a 127.0.0.1 --p 5555
  * --t : d = Direct Broker r = Routing Broker
  * --a : IP Address 
  * --p : Port number
* ps_publisher - start publisher
  * -h : Help - to see argument options
  * Example: python3 ps_publisher.py tcp://127.0.0.1:5556 tcp://127.0.0.1:5555 --t hello --r 100 --d 1.5
  * address - publisher's own address formatted as \<transport>://<ip_address>:\<port>
  * broker address - brokers known address formatted as \<transport>://<ip_address>:\<port>
  * --t : Topics\<string> 0-* topics
  * --r : Random\<int> - number of random messages to send 
  * --d : Delay\<float> - amount of time in seconds before sending messages
* ps_subscriber - start subscriber
  * -h : Help - to see argument options
  * Example: python3 ps_subscriber.py tcp://127.0.0.1:5557 tcp://127.0.0.1:5555 --t hello
  * address - subscriber's own address formatted as \<transport>://<ip_address>:\<port>
  * broker address - brokers known address formatted as \<transport>://<ip_address>:\<port>
  * --t : Topics\<string> 0-* topics
* create_pub_sub.py - utility to start sample publishers/subscribers

<hr>

### APPLICATION PROGRAMMING INTERFACE(API)
#### PUBLISHER
```
Publisher(address = <address of this publisher>, registration_address = <address of the broker>)

register(topic = <string>)
  
publish(topic = <string>, message = <string>, message_type = <default = MessageType.STRING>)
MessageType = [STRING, PYOBJ, JSON]
```

#### SUBSCRIBER
```
Subscriber(address = <address of this subscriber>, registration_address = <address of the broker>)

register(topic = <string>)
  
unregister(topic = <string>)
  
notify(topic = <string>, message = <string>)

register_callback(callback = Function or method to be called when a message is received)

wait_for_msg()

wait_for_registration()
```
* register_callback() provides the application a means of receiving the messages.
* wait_for_message() must be running on the client upon receipt of a message the notify() is called which in turn sends the message details to the registered callback. 
* wait_for_registration() must be run in a seperate thread so that it will not block the subscriber from receiving messages.

<hr>

### TESTING

#### UNIT TESTING
From main project directory
* To run application unit tests

`pytest`
* To run tests and get coverage report

`pytest --cov=pubsub -cov-report html`

<hr>

#### PERFORMANCE TESTING: LATENCY ANALYSIS
- [ ] TODO

<table border=2 align="center">
  <tr>
    <td align="center" colspan="10">ROUTING BROKER</td>
  </tr>
  <tr>
    <td align="center" colspan="10">Publisher Topics (Length)</td>
  </tr>
  <tr align="center">
    <th>Subscribers</th><th>1(short)</th><th>1(medium)</th><th>1(long)</th><th>2(short)</th><th>2(medium)</th><th>2(long)</th><th>3(short)</th><th>3(medium)</th><th>3(long)</th>
  </tr>
  <tr align="center">
    <td align="right">1</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">2</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">4</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">8</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">16</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td border=2 align="right">32</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">64</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">128</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">256</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
   <tr align="center">
    <td align="right">512</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
</table>

<hr>

<table border=2 align="center">
  <tr>
    <td align="center" colspan="10">DIRECT BROKER</td>
  </tr>
  <tr>
    <td align="center" colspan="10">Publisher Topics(length)</td>
  </tr>
  <tr align="center">
    <th>Subscribers</th><th>1(short)</th><th>1(medium)</th><th>1(long)</th><th>2(short)</th><th>2(medium)</th><th>2(long)</th><th>3(short)</th><th>3(medium)</th><th>3(long)</th>
  </tr>
  <tr align="center">
    <td align="right">1</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">2</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">4</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">8</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">16</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">32</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">64</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">128</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">256</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">512</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
</table>

#### Plotted graphs
- [ ] TODO


### REQUIREMENTS
Mandatory: 

- [ ] Use a SingleSwitchTopo with one host per participant in your system (e.g. one host per subscriber, one host per publisher, and one host for the broker). 

- [ ] Start a broker system in either direct or proxy mode
* - [ ] Create a single topic and publish at least 1,000 messages on that topic. Record the time each message arrives on a subscriber
* - [ ] At end of test run, take every latency measurement you have seen so far and calculate the first quartile, the median and the third quartile. This tuple of (mode, count(subs), Q1, median, Q3) is the result of a single test run.
- [ ] Repeat this entire process with 2,4,8,16 subscribers for both direct and proxy mode. You should have 8 tuples (a.k.a 8 rows) when you are done
- [ ] Generate a line graph (INCLUDE AXIS LABELS!!) showing at least the median latency versus the number of subscribers. If your graphing tool supports it, generate a boxplot graph so we can see latency vs subscribers, where latency is drawn as a boxplot instead of a single number. If you need to generate one graph for direct mode and one graph for proxy mode that is OK, but it is preferred to put both lines (or both sets of boxplots) onto one graph next to each other

- [ ] Document what your tests show.
* - [ ] Does the typical time to deliver a message increase as the number of subscribers increases?
* - [ ] How significant is this effect? Does your system become less predictable as the number of subscribers increases (e.g. as count(subs) goes up, do you see the Q1 to Q3 recordings get farther apart?)? 
* - [ ] Do you expect higher latency in subscriber mode vs publisher mode. Peek inside your exact latency measurements - do you see that the first few (or first single) latency measurements are always quite a bit higher than then next ones?
* - [ ] Can you explain this?



Bonus: 

- [ ] Use boxplots in your graphs

- [ ] Come up with a way to scale the above system to much more significant numbers, and expand the test to 32,64,128,256,512

- [ ] Add in a 'warm up' that sends a few hundred messages before it starts recording latency. Be sure you don't pause the system after the warmup is done, you need to keep it running but hot switch into a recording mode

- [ ] In addition to quartile 4, record the maximum value and add that to your boxplot

- [ ] Recreate the graphs

- [ ] Expand your explanatory documentation. See if you observe completely different behavior "to the right of" 16 subscribers, and explain what this means for "reading system results". 
* - [ ] Did you keep the same basic conclusions about system scalability, or did you learn something new?
* - [ ] Does variabilty in message deliver latency scale in an acceptable manner, or does performance degrade so rapidly as the number of subscribers increases that the system is useless at larger numbers?
* - [ ] Consider your system resources - was network or cpu or memory the most scarce resource during your test?
* - [ ] Were you able to run 512 without taxing your local system, or are the results at 512 likely invalid because your host computer was out of resources?
* - [ ] What new information did you learn by looking at the maximum values of the latencies?
* - [ ] For either mode of your system, could you confidently declare an upper limit on message delivery?
* - [ ] If yes, explain that. If no, what would you need to do to guarantee an upper time limit on "event delivered or thrown away"

- [ ] Rerun the test with 4 subscribers, but edit your mininet links manually. Use the `delay='Xms'` option on addLink to make a single link very slow. Play with this scenario. 
* - [ ] Does the single slow subscriber cause the non-slow subsribers to starve? Is the publisher slowed down? 
