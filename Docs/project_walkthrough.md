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

###3.Versatile - Consider graphs, trees, DNFs and groups, what do they have in common? The answer is they can all be represented by some circles connected by lines/arrows. So when we should define one object(preset) in our software that makes all of these mathematical objects easy to create. In other words, we want a higher level of abstraction for our core objects so that they have potential to become an assortment of things.

Despite all of this, I am not suggesting that we should not put lots of presets in the software. We can put as many presets as we want, as long as they are organized and kept hidden from the user most of the time, like Excel's library of functions (e.g. AVERAGE, STDDEV).

## What is our goal?
Our short term goal is to carve out the details of the design more, and implement the software on web platform. The long term goal would be to reach collaboration with one or more professors in CMU, so that they can put our software to use in teaching. An even greater goal would be to cooporate with knowledge-spreading websites like Expii, Quora and Stack Exchange and make our app a plugin for their editor so that millions of people can use our software to learn and spread their insights.

## What are we going to make?
###Features:
####Object based

####Slide based animation
There is a slide that the user is currently editing (the working slide) and a list of slides that are saved in temporal order (the timeline). When the user finishes editing the working slide, s/he can save (which is just making a copy of) the working slide to the timeline. Then the user can keep on editing the same working slide. In this way the work flow is fluent and uninterrupted.
When the user playes the animation, Presimation will generate the animation between two consecutive slides based on an interpolation (linear or otherwise specified by user) of indentical objects in the two slides. If an object in the second slide does not exist in the first slide, an entrance animation will be generated automatically; similarly if an object gets deleted in the next slide, an exit animation will also be generated.

####Object menus
In contrast to the "attributes" panel that is a part of the layout in most other softwares, Presimation uses pop-up menus that toggles when the user double-clicks on the object. Hopefully this design will make the interface cleaner and not full of irrelevent information.
The object menus contain all the information that can be used to manipulate the object
####Action based programming
###Tools:
####Circle tool
####Pointer tool
####Marker tool
Area tool (feature: make intersection/union of areas)

## What are the users going to make?
Sorting algorithms: bubble sort