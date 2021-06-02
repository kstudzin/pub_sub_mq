# cs6381-assignment1: Single Broker Publish-Subscribe

## API

### BROKER CONFIGURATION

* PUBLISHER -> ROUTINGBROKER -> SUBSCRIBER
All message passing goes through routing broker.

* PUBLISHER -> DIRECTBROKER -> SUBSCRIBER
Direct broker holds registry to all publisher to send messages directly to subscriber.


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
  
* Latency analysis
  
* Plotted graphs
  
