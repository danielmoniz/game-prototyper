
About
=======

game-prototyper is a tool designed to speed up the creation of card and board
games. The user creates spreadsheet data files (CSV) that include all necessary
information for each of their cards/entities. They create card templates that
take advantage of HTML and CSS to render text and images in high quality.
Images can be saved in the resources directory of the project. These cards are
then displayed in the browser, alternating between front and back pages to
allow for printing double-sided cards.

A browser's (Chrome is preferred) print-to-pdf feature can be used to
generate a printable PDF.

The project contains a script that pulls icons from thenounproject.com if you
supply a set of free and easily-acquired credentials. This greatly minimizes the
time spent creating a polished game and kick-starts the design process.

Who is this for?
================

game-prototyper is for anyone creating a card game or board game that is
willing to take the time to learn a bit of HTML and CSS. It is far faster to
update information in a spreadsheet file and run a script than it is to modify 
each card individually every time changes are made.

Technology
===========

This project uses a basic web stack to generate the cards and requires a
browser to render them. Google Chrome is highly recommended because the print
feature relies on page breaks when used print-to-pdf.

How to install
==============

Open a terminal and run:
    git clone https://github.com/danielmoniz/game-prototyper
    cd game-prototyper
    pip install -r requirements.txt

How to run
===========

Open a terminal and run:

    python server.py

Then open a browser and navigate to the URL:

    http://127.0.0.1:5000/your_project_name

Try this with the sample project to get immediate output of cards:

    http://127.0.0.1:5000/your_project_name/?duplicates=false

Image/Icon bootstrapping
=======================

in order to populate your project with icons, use the image_bootstrap.py script found
in the directory. Simply running

    python image_bootstrap.py

will use the lists of goods/resources/etc in the goods.txt and other_icons.txt
files for your project. It can, however, be provided with a number of options
such as pulling fewer or more images, using public domain only, etc. Just run

    python image_bootstrap.py --help

to see the list of options available.
    

Compatibility
=============

Currently, Compatibility with Windows is not offered. This is largely due to a
lazy use of forward slashes. If someone wants to open a pull request to remedy
this, I would be happy to accept it.






Examples
========

Note that all images in the below examples are attributed in
sample_project/attributions.txt . All icons seen were collected via the image
bootstrapping script. Thanks to Jonas De Ro (http://jonasdero.deviantart.com/)
for the fantastic medieval artwork.

![alt tag](https://raw.github.com/danielmoniz/game-prototyper/master/sample_project/samples/drought.png)
![alt tag](https://raw.github.com/danielmoniz/game-prototyper/master/sample_project/samples/fishing nets.png)
![alt tag](https://raw.github.com/danielmoniz/game-prototyper/master/sample_project/samples/irrigation.png)
![alt tag](https://raw.github.com/danielmoniz/game-prototyper/master/sample_project/samples/score sheet.png)
![alt tag](https://raw.github.com/danielmoniz/game-prototyper/master/sample_project/samples/seasons.png)
![alt tag](https://raw.github.com/danielmoniz/game-prototyper/master/sample_project/samples/legend.png)

