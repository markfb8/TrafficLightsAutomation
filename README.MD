# SupermarketQueueSimulation 
This is a python Event Based simulation implementation of a store formed by 1 queue, 4 supermarket checkouts and 3 possible types of customers:

- Customer with few products (less use time)
- Customer with some products (medium use time)
- Customer with lots of products (long use time)
  
If any of these wait for more than 15 minutes in the queue they leave.

To execute the simulation just run scheduler.py and introduce the requested configuration parameters.
Simulation should stop at the specified simulation time, but it may stop on its own when no more events remain in the events list. 