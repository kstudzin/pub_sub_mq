# cs6381-assignment1: Single Broker Publish-Subscribe

## API

### BROKER CONFIGURATION

* PUBLISHER -> ROUTINGBROKER -> SUBSCRIBER

All message passing goes through routing broker.

* PUBLISHER -> DIRECTBROKER -> SUBSCRIBER

Direct broker holds registry to all publishers to send messages directly to subscriber.

### FILE DESCRIPTORS

* folder - cs6381-assignment1
  * folder - pubsub
    * __inin__.py - 
    * broker.py - 
    * publisher.py -
    * util.py - internal helper file
  * folder - tests
    * test_direct_broker.py - units tests
    * test_publisher.py - units tests
    * test_routing_broker.py - units tests
    * test_subscriber.py - units tests
  * create_pub_sub.py - 
  * psserver.py - CLI to start direct or routing broker

### COMMAND LINE INTERFACE USAGE
#### API USAGE
* psserver.py - start broker type: Example parameters (--t r --a 127.0.0.1 --p 5555)
  * --t : d = Direct Broker r = Routing Broker
  * --a : IP Address
  * --p : Port number

* create_pub_sub.py - utility to start sample publishers/subscribers

#### UNIT TESTING
* pytest /tests


### PUBLISHER
```
Publisher(address = <address of this publisher>, registration_address = <address of the broker>)

register(topic = <string>)
  
publish(topic = <string>, message = <string>, message_type = <default = MessageType.STRING>)
MessageType = [STRING, PYOBJ, JSON]
```

### SUBSCRIBER
```
Subscriber(address = <address of this subscriber>, registration_address = <address of the broker>)

register(topic = <string>)
  
unregister(topic = <string>)
  
notify(topic = <string>, message = <string>)

register_callback(callback = Function or method to be called when a message is received)

wait_for_msg()

wait_for_registration()
```
  
### TESTING
  
#### LATENCY ANALYSIS

<table align="center">
  <tr>
    <td align="center" colspan="10">ROUTING BROKER</td>
  </tr>
  <tr>
    <td></td><td align="center" colspan="9">Publishers</td>
  </tr>
  <tr align="center">
    <td>Subscribers</td><td>1</td><td>5</td><td>10</td><td>20</td><td>50</td><td>100</td><td>200</td><td>500</td><td>1000</td>
  </tr>
  <tr align="center">
    <td align="right">1</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">5</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">10</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">20</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">50</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">100</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">200</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">500</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">1000</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
</table>

<table align="center">
  <tr>
    <td align="center" colspan="10">DIRECT BROKER</td>
  </tr>
  <tr>
    <td></td><td align="center" colspan="9">Publishers</td>
  </tr>
  <tr align="center">
    <td>Subscribers</td><td>1</td><td>5</td><td>10</td><td>20</td><td>50</td><td>100</td><td>200</td><td>500</td><td>1000</td>
  </tr>
  <tr align="center">
    <td align="right">1</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">5</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">10</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">20</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">50</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">100</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">200</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">500</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
  <tr align="center">
    <td align="right">1000</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
</table>


#### Plotted graphs
  
