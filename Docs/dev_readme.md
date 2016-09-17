# Developer README

Welcome to the `Presimation` team! This is where I will 

## Developer tools
There are many useful development tools we can use to make life easier.

#### Green VPN
For folks in China mainland it is imperative to get a VPN and ask questions on
google. [GreenVPN][1] is stable in China mainland and has unlimited bandwidth.

#### RESTful client
As a chrome extension, [Advanced REST Client (ARC)][2] serves as a good testing
platform without actually implementing the client side.

[1]: http://www.hao162.com/
[2]: https://chrome.google.com/webstore/detail/advanced-rest-client/hgmloofddffdnphfgcellkdfbfbjeloo?utm_source=chrome-app-launcher-info-dialog

## Knowledge, APIs, SDKs

Check these terminologies out on wikipedia!

1. RESTful
2. HTTP
3. socket
4. JSON
5. markdown documentation (what you are reading QVQ)

Check out the following APIs/SDKs on github!

1. parse-server
2. flask

## Function return values for error handling
It is important to know if our function exited with success or not.  
Here we use the convention:  
```python
return -1            # Invalid arguments
return 0             # Function exited properly
return ANY_OTHER_INT # Function exited with error code ANY_OTHER_INT
```
Error handling should be everywhere in your contributed code so that it is easy
to identify what went wrong in such a big chunk of code.

#### Proposed reserved return values
```
2000: Insufficient System Resources including CPU, RAM, Storage, etc.
2001: Network error
2002: User aborted command
```

## Documentation, Coding Style and Comments
#### Documentation and Comments
As a team collaborator you should bear in mind that your code should be readable
to your teammates. The good practice is to leave useful comments, and write a
good API documentation for functions exposed to your clients.

#### Coding Style
1. Avoid lines that exceed 80 characters.
2. Function names: useCamelCase.
3. Global/static variables should be CAPITALIZED_WITH_UNDERLINE.
4. Local variables should be lowercase. Use of hyphens is prohibited as they
might be reserved.
5. A function should specify and honor its contracts.
6. Modular coding is recommended. Always avoid duplicate code.
7. Whatever good practices you have always been doing!

## Issue Management
By complying to the listed issue tracking system the team can better manage
issues that arise during development. The general format is XI-NNNN where X
is the realm of issue and NNNN is the issue number.

#### SI - Science Issue  
Issues such as physical implementation of a reliable solenoid; whether magnetic
surfaces can be used as signal transducting electrodes, etc.

_Example:_  
**Title:**  
SI-0023: Magnetic attaching charging port with embedded signal electrodes  
**Content:**  
Changing magnetic flux may cause signal disruption on magnetic surface, and may
undermine the reliability of signal interface.

#### MI - Mechanical Issue  
Issues that are related to mechanical problems such as gear ratio of a gearbox;
specs of motors; omni-direction drive mechanism, etc.  

#### EI - Electronic Issue
Issues that are related to electronics, such as the motor driver.  

#### AI - Algorithm Issue
Issues that are related to computer science, algorithm, such as swarm algorithm;
localization algorithm; QR code analyzing algorithm, etc.

#### FI - Framework Issue
Issues that are related to framework, system, data flow, etc.

#### UI - User Interface Issue
Regarding UX Design, user experience, identifying user needs, etc.

#### GI - General Issue
General issues include discussions about new features to be added; financial
budget; timeline; etc.


## Terminologies and Definitions  

**looper:** It is a small flat robot that travels in warehouse and fetches
shelves and then carries them to designated locations for further processing.  

**TH3-MA1N:** Aka. the main algorithm, this algorithm keeps track of all running
robots and updates them with new general orders such as destination, instruction
and tells loopers others' locations.  

**S.W.A.R.M. :** The algorithm that runs on each looper which decides specific
path to take.

**infinite-loop:** This is the project name, resembling the infinite loop of
loopers running in warehouse that walk loops around before yet another loop.  

## Structure and Dataflow
**On Main Server:**  
| Database | <-> | Server Backend (parse-server) | <-> | TH3-MA1N |

**Then:**  
| TH3-MA1N | <--wirelesss--> [ Looper1, Looper2, ... ]

**At Each Looper:**  
{ General Instruction  } -> S.W.A.R.M. <-> | Looper API | <-> | Hardware |  
_Feedback to TH3-MA1N:_  
S.W.A.R.M. -> | Looper API | <-> | Comms Module | <--wireless--> | TH3-MA1N |

**Remark**

"TH3-MA1N" will tell loopers their destinations and give them knowledge about
their operations. However, as the main algorithm it does not babysit each
looper. Instead, each looper itself will decide its route to destination based
on traffic, priority, and other parameters; loopers will stop once they think
it is likely to encounter another looper in a foreseeable furure.

A looper might see all other loopers, and 3 unit steps of all loopers for
swarm coordination. A looper will know about the traffic condition real time
so that it can optimize its path. A looper will always updating its location to
"TH3-MA1N".
