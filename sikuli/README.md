# Sikuli Scenario

In this folder, you can find the Sikuli project "canopsis". It contains all functional
tests for main Canopsis use cases.

## How-to run

First, you need to install Sikuli :

    # apt-get install sikuli

Be sure you have a web-browser which is pointing to your Canopsis instance.
Run the script ``canopsis.sikuli/filldata.py`` (needs the python module ``kombu``)
to generate data for the Sikuli scenario.

Then, from this folder, you can run the scenario with the following command :

    # sikuli canopsis.sikuli

## TODO

- improve filldata.py
- write scenarios for all use cases