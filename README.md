# CatCam

This is a simple python script I created to setup a web cam to watch my cat's automatic feeder when I'm away. This runs on a Raspberry Pi 3 Model B+ connected to a Logitech USB camera I had sitting around.

This takes a picture every so many minutes and copies the image to a S3 bucket. This also creates a index html file which shows all the pictures taken each day.

### To setup:

1. Install pip: 
    ```
    sudo apt install python3-pip
    ```
2. Install web cam software: 
    ```
    sudo apt install fswebcam`
    ```
3. Clone the repo:
    ```
    cd ~
    git clone git@github.com:patleahy/catcam.git`
    ```
4. Create a virtual environment in the catcam folder: `
    ```
    cd ~/catcam
    virtualenv -p python3 .
    source bin/activate
    pip install -r requirements.txt
    ```
5. Setup an s3 bucket with [static web hosting](https://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html).

6. Configure AWS credentials, edit `~/.aws/credentials`:
    ```
    [default]
    aws_access_key_id=xxx
    aws_secret_access_key=yyy
    ```

7. Setup a cronjob to take a picture every 5 minutes:
    ```
    */5 * * * * ~/catcam/bin/python ~/catcam/catcam/snap.py <s3bucker> <s3folder> 1>>~/catcam/log/snap.log 2>&1
    ```
    Note that the fswebcam often fails to take a picture. To work around this I retry 4 times, waiting 1 minute between tres. It usual works on the second try. Because I retry for 4 minutes, setting the corn job every 5 minutes is a good idea.

8. View the pictures at http://s3servcer/s2bucket/s3folder/year/month/day/index.html. Since this is public I use a folder people can't guess, e.g. https://s3-us-west-2.amazonaws.com/catcam.mybicket/5c2c7e1e-19fd-11ea-978f-2e728ce88125/2019/11/29/index.html.
