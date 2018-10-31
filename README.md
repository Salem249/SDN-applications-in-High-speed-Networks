<!---
/*
 *
 * AUTHORS: Salem Masoud (s.masoud@campus.tu-berlin.de)
 * 			Ahmad Alaswad (Alaswad@campus.tu-berlin.de)
 *
 */
-->

# SDN applications in High speed Networks](https://gitlab.tubit.tu-berlin.de/it249/SDN_applications_in_High-speed_Networks)

TThis Project was carried on as the property of SDN Lab course’s assignment, under the supervision of Dr.-Ing. Hagen Woesner in Telecommunication Networks Group (TKN) at TU Berlin.

A Switching loop happens in computer networks when there is more than one Layer 2 (OSI model) path between two endpoints. This loop generates broadcast storms as broadcasts and multicasts are forwarded by switches out every port, the switches will repeatedly rebroadcast the broadcast messages flooding the network. Since the Layer 2 header does not support a time to live (TTL) value, if a frame is sent into a looped topology, it can loop forever.
This project provided solutions for overcoming a loop between three switches by carrying on two implementations; the first is based on Spanning Tree Protocol (STP) and the second is a network graph implementation based on a Python package called NetworkX. Both solutions will be implemented on an SDN controller called RYU.

# Dependency
The following software and libraries and their dependency have to be installed:
1- Ryu SDN Framework
https://osrg.github.io/ryu/

2- Mininet
http://mininet.org/


# Usage
TBC



# Contributors
In random order:

    * Ahmad Alaswad (Alaswad@campus.tu-berlin.de)
	* Salem Masoud (s.masoud@campus.tu-berlin.de)
