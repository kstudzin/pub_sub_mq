# cs6381-assignment1: Single Broker Publish-Subscribe

## API

### BROKER CONFIGURATION

* PUBLISHER -> SUBSCRIBER

* PUBLISHER -> BROKER -> SUBSCRIBER


### PUBLISHER
```
register_pub (topic = <some string>, <some identification of the publisher>)
  
publish (topic = <string>, value = <val>)
```

### SUBSCRIBER
```
register_sub (topic = <some string>, <some identification of the subscriber>)
  
unregister_sub (topic = <some string>, <some identification of the subscriber>)
  
notify (topic = <string>, value = <val>)
```
  
### TESTING
  
* Latency analysis
  
* Plotted graphs
  
