# ParserMTSTravelHotel
Parsing of hotels and their rooms from the MTS website https://travel.mts.ru/

Selenium-wire is used for parsing the site in order to intercept asynchronous requests after initializing the hotel/room search link.
Edge was chosen as the web driver for selenium to avoid blocking by the site. There were many attempts to use the chrome driver (user agents were changed, automated software and browser fingerprint options were disabled, the binary of the web driver executable itself was changed), but there were no results, access was blocked.
To get started, you need to:
1) Install the Edge browser of a certain version
2) Install the Edge web driver of the same version
3) Place the web driver in the drivers folder
4) Change in config.py paths to the driver and cookies

The parser outputs basic data, but it can be expanded by following JSON.
