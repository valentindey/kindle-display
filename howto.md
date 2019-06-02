# How to make a kindle 4 NT "smart display"

To make my old kindle 4 no touch display some information, I took the following steps.

If you are interested in reproducing this and encounter problems or find errors in my
explanation, feel free to drop me a line.

Some of the steps below come with a risk of rendering your device unusable.
I do not take any responsibility if that happens!

### preparation

For a clean start, I did a factory reset of the kindle and updated its software to the
most recent version, 4.1.3 at that time.
Check [amazon's page](https://www.amazon.de/gp/help/customer/display.html?nodeId=200774090)
on how to do the software update. Depending on the version installed a step wise update
may be necessary.

After that, I did jailbreak the kindle and installed the "usbnetwork hack" as described
[here](https://wiki.mobileread.com/wiki/Kindle4NTHacking)
In a [linked post](https://www.mobileread.com/forums/showthread.php?t=88004) I also found
a package to install python2.7 on the device.
In general the mobileread wiki and forums are a great resource for this kind of things.

### ssh

To be able to connect to the device via SSH, I edited the file `usbnet/etc/config` such that
the corresponding lines read

    K3_WIFI="true"
    USE_OPENSSH="true"  # just a preference, not really necessary

*WARNING* this file needs UNIX line endings, Windows people watch out!

On the device open the keyboard and execute type the two following commands
   
    ;debugOn
    ~usbNetwork

Now I was able to log in via ssh

    ssh root@<YOUR_KINDLE_IP_HERE>

For the password, I was able to calculate the one for mine with [this online tool](https://www.sven.de/kindle/).

To not always having to type the password you can copy your public key over:

    ssh-copy-id root@<YOUR_KINDLE_IP_HERE>

This copies the file to `/var/tmp/root/.ssh/authorized_keys` but it's needed at `/mnt/us/usbnet/etc/authorized_keys`
So log in once again (with password) and move it:

    mv .ssh/authorized_keys /mnt/us/usbnet/etc/

After that ssh should not ask for a password anymore.

### dependencies

The code to generate the display image is written in python with one dependency:
[`pytz`](https://pypi.org/project/pytz/).
I figured the most simple way to install it was via pip, so I did that.
Downloading the [pip installation script](https://bootstrap.pypa.io/get-pip.py)
on the device did not work for me (and I didn't bother to further investigate)
so I downloaded it on my laptop and `scp`ed it over.
On the kindle I then installed pip with `python get-pip.py` and `pytz` with
`/mnt/us/python/bin/pip install pytz`
    
For converting SVG images to PNG, I used the rsvg-convert package shared by "brianinmaine"
in [this mobileread thread](https://www.mobileread.com/forums/showthread.php?p=2743269)
and copied it over to the kindle to `/mnt/us/extensions`

For further processing the PNG image to make the kindle properly display them, `pngcrush`
seems to be the means of choice.
I could not find a working version for the kindle so I had to compile it myself.
I downloaded the source from https://pmt.sourceforge.io/pngcrush/ and compiled it on my laptop with `arm-linux-gnueabi-gcc`
Note that version 1.6.10 was the latest one I got to work on the kindle.
I had to replace `long` for `__PTRDIFF_TYPE__` in line 33 of `zutil.h` (based on [this](https://sourceforge.net/p/pmt/bugs/75/#4408))
Also, I had to move the `libdl.so.2` in `extensions/rsvg-convert/kindle-lib/`.
I'm not sure why that was a problem, though.

### putting it all together

To make use of all this an image to display needs to be generated.
I used python for this to generate a SVG image, see the code in this repository.
All of it goes to the kindle

    cd kindle-display
    scp -r kindle-display root@<YOUR_KINDLE_IP_HERE>:/mnt/us/extensions

and on the kindle framework and power deamons are stopped and a new cronjob is started

    mntroot rw  # make the root filesystem writeable to be able to edit the crontab file
    cd /mnt/root/extensions/kindle-display
    ./start_display.sh

To remove the cronjob, `remove_cronjob.sh` can be used.

This calls the `display.sh` script which

* generates an SCG file with `generate_svg.py`
* converts it to PNG with `rsvg-convert`
* "crushes" the PNG with `pngcrush`
* displays it with the builtin `eips` command

Note that the cronjob is run and updates the screen every minute.
If for some reason the kindle is started again you'd have only this one minute to enable usbnetwork again with
    
    ;debugOn
    ~usbNetwork

### notes

The weather data is polled from the openweathermap API and I get munich public transportation information
from the MVG API.
