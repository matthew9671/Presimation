#Presimation Project Walkthrough
Welcome to Presimation! Hopefully this document can help you understand what Presimation is and how we are going to approach making it. I will cover the list of features and some examples of animated presentations that can be made with them. Of course, as we gather more ideas, this document will also be updated.

## What is Presimation?
A combination of presentation and animation, Presimation is (or will be) a web app that allows users to build a variety of animated presentations for the purpose of spreading knowledge. In other words, it's like flash combined with powerpoint.

## How is it different?
Presimation has lots of similarities with many software out there. However all of these software are either too complicated to use for teaching purposes (like Flash or Mathematica), or too specialized (Geometric Sketchpad, visualgo.net). 
Powerpoint/Keynote/Google Slides is what most instructors use, but making simple informative animation in it is really painful, not to mention more sophisticated ones that involves numerical manipulations. This is where Presimation comes in.

## What is our design phliosophy?
In order to make the software easy to learn and use for non-programmers, it follows naturally that we should avoid demanding the users to write code (not that we can't have any coding at all). Apart from that, these are also essential:

###1.Clean interface
 - Since we don't expect users to make animated movies or tweak a thosand parameters, the interface should be really succinct, hiding away many options and features the users don't want to see all the time.

###2.Fluent to use
 - Just draw stuff, take a snapshot, change what you've drawn, and take another snapshot. If you want to make more complicated stuff, just specify the interactions you want between elements, and let it play out.

However, we do want our product to be able to make a large variety of Presentations, as that is the main point of our project:

###3.Versatile
 - Consider graphs, trees, DNFs and groups, what do they have in common? The answer is they can all be represented by some circles connected by lines/arrows. So when we should define one object(preset) in our software that makes all of these mathematical objects easy to create. In other words, we want a higher level of abstraction for our core objects so that they have potential to become an assortment of things.

Despite all of this, I am not suggesting that we should not put lots of presets in the software. We can put as many presets as we want, as long as they are organized and kept hidden from the user most of the time, like Excel's library of functions (e.g. AVERAGE, STDDEV).

## What is our goal?
Our short term goal is to carve out the details of the design more, and implement the software on web platform. The long term goal would be to reach collaboration with one or more professors in CMU, so that they can put our software to use in teaching. An even greater goal would be to cooporate with knowledge-spreading websites like Expii, Quora and Stack Exchange and make our app a plugin for their editor so that millions of people can use our software to learn and spread their insights.

## What are we going to make?
###Features:
####Objects
Everything that the user creates in the workspace is an __object__. Objects have a list of attributes that can be displayed and edited in their pop-up menus. __Slides__ (frames) are just a couple of methods in addition to lists of objects.

####Slide based animation
There is a slide that the user is currently editing (the __working slide__) and a list of slides that are saved in temporal order (the __timeline__). When the user finishes editing the working slide, s/he can save the working slide to the timeline, or, _take a snapshot_. Then the user can keep on editing the same working slide. In this way the work flow is fluent and uninterrupted.
When the user playes the animation, Presimation will generate the animation between two consecutive slides based on an interpolation (linear or otherwise specified by user) of indentical objects in the two slides. If an object in the second slide does not exist in the first slide, an entrance animation will be generated automatically; similarly if an object gets deleted in the next slide, an exit animation will also be generated.

####Object menus
In contrast to the "attributes" panel that is a part of the layout in most other softwares, Presimation uses pop-up menus that toggles when the user double-clicks on the object. Hopefully this design will make the interface cleaner and not full of irrelevent information.
The object menus contain all the information that can be used to manipulate the object, but not all of them needs to be shown to the user. 
Firstly, the attributes are divided into different tabs, so each tab does not have to contain too many elements. 
Secondly, there are _hidden fields_ in the menus that are basically "additional information" that only comes up when the user double clicks on some other field. For example the "highlight" field is a visible field, but the "highlight pattern" that decides which kind of highlighting will be used is hidden, and users can toggle it when they actually care about how to highlight the object. 
Thirdly, some sets of fields controlling the same appearence/behavior of an object might be interchangeble. For example a color can be picked both with the RGB representation or the hue-saturation-brightness representation. When trying to pinpoint a color, you might use the previous, but when you want to draw a rainbow you will definitely prefer the latter. We will put in a switch button to switch between these kinds of _interchangeble fields_ so that the users can enjoy the benefit of all of them without the interface being too crowded.

There are also a few features that help the user with editing an object's attributes.
####Expressions in attributes
An object's expression

####Graphical editing
With the object menus, the users can manipulate and code on every attributes of the object. But there will be an easier way to do it, which is dragging on the handles of the object (just like any other similar software). In programming, when the user wants to get a handle of some other field or object, s/he can simply click on the icon of the current field and drag to the target object and field (A similar feature is common in Adobe After Effects and Unity3D). With these features, the users can operate the software much more fluently.

####Action based programming
One of the drawbacks in the Presimation Demo is that programming is still heavily reliant on writing code, and the code is normally not visible so that the user can get confused. In the official build of Presimation we can use action based programming to solve these problems. The idea is we should put all the code (in the form of __action__s) in the slides instead of in the objects, and display them to the user in a panel on the interface (just like the "animation" panel in Powerpoint). The actions are lines of codes presented visually as blocks. The users program by assembling the blocks in the actions panel into a list of actions. Every time the user takes a snapshot (or re-applies the action list to the slide), the list of actions are applied to the objects in the list, changing their attributes. 
Note that after the action is applied, the slide is static and animation works just like if there were no programming involved. For example when you are building bubble sort, just create the objects and actions in the working slide, then repeatedly take snapshots (save frames) until the animation is complete.

###Objects/Tools:
####Circle tool:
Drag and draw a circle on the workspace. The drag starting point is the center of the circle.
####Rect tool:
Drag and draw a rectangle on the workspace. The positions of the rectangle is represented by a interchangable field:
1. Top left corner position & bottom right corner position
2. Center position & width and height
3. Left, bottom, width and height
For developers: note that this tool is a little tricky to implement since the status (bl, br, tl, tr) of each corner could change when the user manipulates the rectangle.
When the user switches between the interchangable fields, the handles on the objects should also change accordingly.
####Pointer tool
Click on any existing object (including pointers) to create a pointer to that object. Pointers can be dereferenced by a Do Block called get object. The default setting to the Do Block is follow the pointers to the end until you get a non-pointer, but we can make this adjustable.
Another Do Block that you use on the pointer all the time is increment/decrement. The pointer is on the entire series of objects, so incrementing it will cause it to go to the next object in the list. If there are no more objects it will either do nothing or go back to the first element by setting. (__***More thoughts needed***__)
####Group tool
Drag-select (or circle-select) a group of objects to create a group object. 
The group object has a lot of applications: 
1. It can be treated as one object, setting any of its fields will result in changing the corresponding field in every object in the group. Note that a group can contain objects of different kind, so the attributes of the group will be the intersection of all the attributes of the objects (with the exception of NAME and INDEX).
A (more powerful but more confusing) alternative would be to have the value of every field be a variable (dependent on which object it is). If the user deletes that varible and writes a constant, it will be the same as the first implementation. But if the user instead uses the varible to write an expression, it will be applied to all the objects in the group. For example you can use this method to offset every object to the right by 10 without changing their relative position.
2. There also should be many presets for users to use. E.g. "align in straight line", "align in circle", "align in grid" etc.
3. If there can be a way to assign an index to every object in the group, then the users can do even more powerful things with the group object. However this is probably way too complicated and confusing.
####Marker tool
Click in the workspace and create a marker object. If this object moves, it will leave a colored trail in its trajectory. Can be used to present parametric curves, etc.
Best used in conjuction with the "Follow" block.
####Camera tool (__***More thoughts needed***__)
This is still just an idea, but it would be cool if we enable users to make the presentation zoom in on some portion of the workspace (like Presi), or even create a split-screen effect.
####Area tool (__***More thoughts needed***__)
feature: make intersection/union of areas which can be filled and highlighted.
Useful for presenting probability, set theory and many more!
Note to developers: Algorithm might be non-trivial, and there probably are some algorithms out there that can realize this.

###Actions:
Each line of action consists of different kinds of blocks. The different kinds of blocks are represented by differently colored outlines.
Benefit of this? -No syntax errors; well typed functions don't go wrong!
#### Object Blocks (orange outline)
Drag from the grabber to a object in the workspace to create an object block.
#### Field Blocks (green outline)
With an object block in place, a field block can be choosen and added from the object's fields.
#### Do Blocks (grey outline)
* Set to(Object, field, value) - Set a field of an object to a value
* Object: Free([Field]) - Break the dependence of a field in any object (clear the expression in the field); if no field is provided, all field's dependence will be broken.
* Swap(Object, Object, field) - Swap the values of fields of two objects.
* Object: Count() - Return the number of objects in the series of objects.
* Pointer: Increment() (Can set step and change to decrement in setting)
* Pointer: Get()
* Group: Shuffle(Field) - Shuffles a field in the group of objects
Follow(Object, Object) - Makes the first object follow the second one. When the position of the second object changes, the position of the second object will change accordingly to make the relative position the same. Note that the position of the first object can be actively changed. 
The function of this block can be realized in other ways, but we can have it for convenience. This block will mostly be used for markers.
* Marker: Clear() - Clear the trajectories drawn by the marker.

#### Flow Blocks (red outline) (__***More thoughts needed***__)
If

## What are the users going to make?
###[Computer Science]Bubble Sort:
1. Create a rectangle. Set the position representation to "left bottom height width" and set the height to "10 + index * 10" by grabbing or just typing the expression.
2. Hold down the "d" key, click and drag to copy the rectangle n times [1]. These rectangles will be the numbers to sort. Note that the height of each of the rectangles will be different because of the expression.
3. Select all the objects with Group Tool, double click on the group generated to expand its menu and click "align in line". Double click on the "align" icon to pop the hidden fields, and in it specify the spacing between objects.
4. In the actions panel, grab the group object to create an Object Block. Create a shuffle do block and attach the "height" field to it. Click "apply", the height of all the rectangles should be randomized.
5. With the pointer tool, double click on any of the rectangles to create a series of pointers that points to each one of the series of objects. [2] These pointers represents the slots in the list that we are sorting.
6. Create two more pointers that points to the first pointer in the series created in the previous step. These points to the low and high positions in our list. Grab the first pointer in the action panel and add an _Increment_ Do Block on it. Everytime we take a new snapshot the pointer will move forward. In the settings for the Do Block, set the _loop range_ from 0 to _count_-2.[3] In the second pointer's menu set the _point to index_ field to that of the first pointer's +1. (This step is rather complicated, maybe we could do better without losing generality?)
7. Finally at the last step! Create an _if_ Flow Block, and in the condition choose ">". For the first argument select the "low" pointer, choose the _Get_ Do Block to get the rectangle that the pointer that the pointer is pointing to is pointing to (lol) and choose the _height_ Field Block. Do the same thing for the "high" pointer in the second argument. The condition is satisfied when the first number is greater than the second number, and now we would like to swap them. In the body of the if block, build the expression: 
~~~~
swap(low.get(), high.get(), "left")
swap(low, high, index)
~~~~

And we're done! Just take a bunch of snapshots and watch the list sort itself![4]

[1]: This is what I used in the demo. In the final product we might consider a do block that when applied to an object generate n copies of that object.
[2]: This is a big improvement from the demo as you have to set up the pointers manually.
[3]: By default this is set to _count_-1 so when the pointer reaches to the end of the list it returns to the first one.
[4]: Note that the shuffle action is by default one-time, so when you create a new snapshot it will just go away. The other actions stay and are repeated everytime a new snapshot is taken.
