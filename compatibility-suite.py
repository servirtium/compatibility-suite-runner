import sys
import os
import signal
from pathlib import Path

import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import subprocess
import time
import argparse

docker_image_name = Path('.compatibility_suite_docker_image_name.txt').read_text()

parser = argparse.ArgumentParser(description='Run Servirtium Standalone Server and Compatibility Suite')
parser.add_argument("mode", help="Servirtium's mode of operation, i.e. recording a new script or playing an existing one back", choices = ["record", "playback", "direct"])
parser.add_argument("-p", "--port", help="The port Servirtium will run on", type=int, default=61417)
parser.add_argument("-d", "--chromedriver", help="The location of the Selenium Chrome Webdriver executable - omit to use one that's on the system PATH")
parser.add_argument("-t", "--testpage", help="The page to point chrome at to run the tests, use the '%%s' token where the port should be specified. To point back at the original todobackend, specify http://www.todobackend.com/specs/index.html?http://localhost:%%s/todos", default="https://servirtium.github.io/compatibility-suite/index.html?http://localhost:%s/todos")
parser.add_argument("--backend", help="The real todo backend implementation, only used in 'record' or 'direct' mode", default="http://todo-backend-sinatra.herokuapp.com")
parser.add_argument("--timeoutseconds", help="Number of seconds to wait before giving up on a successful run and ending the test run", type=int, default=25)

args = parser.parse_args()

browser_url = args.testpage %(args.port)

docker_container_name = "servirtium-compatibility-test-%s" %(args.mode)

if args.mode == "record" or args.mode == "playback":

    dockerInfo = subprocess.Popen(["docker", "info"], stdout=subprocess.PIPE)
    result = str(dockerInfo.communicate()[0])
    if "Is the docker daemon running?" in result:
        print("ERROR: Docker Daemon needs to be running - start it please.")
        exit(10)

    subprocess.call(["docker", "volume", "create", "scripts"])
    subprocess.call(["docker", "rm", docker_container_name, "-f"])
    docker_args = ["docker", "run", "-p", "%s:%s" %(str(args.port), str(args.port)), "--volume", "scripts:/Servirtium/test_recording_output", "--name", docker_container_name, "-d"]
    # TODO check that servirtium docker process is already started.
    subprocess.call(docker_args + [docker_image_name, args.mode, args.backend, str(args.port)])
    print("Docker container: %s" %(docker_container_name))

else:
    print("showing reference Sinatra app online without Servirtium in the middle")
    browser_url = "http://www.todobackend.com/specs/index.html?%s" %(args.backend)

chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--proxy-server=%s" % "localhost:%s" %(args.port))
chrome_options.add_argument("--auto-open-devtools-for-tabs")


if args.chromedriver:
    chrome = webdriver.Chrome(executable_path=args.chromedriver, options=chrome_options)
else:
    chrome = webdriver.Chrome(options=chrome_options)

time.sleep(5)

chrome.get(browser_url)
start = time.time()

while True:
    number_of_passes = int(chrome.find_element_by_class_name("passes").text.replace("passes: ", ""))

    try:
        error_class = chrome.find_element_by_class_name("error").text
    except NoSuchElementException:
        error_class = ""

    if number_of_passes == 16:
        print("*** Compatibility suite: all 16 tests passed ***")
        print("Closing Selenium")
        chrome.quit()
        break

    if "ERROR" in error_class:
        print("*** Compatibility suite: did finished with " + str(number_of_passes) + " instead of 16 passes as expected. See open browser frame and 'ERROR' in that page ***")
        break

    if (time.time() - start) > 45:
        print("*** Compatibility suite: Timed out after 45 seconds. See open browser frame. ***")
        break

    time.sleep(1)

# TODO warn that docker process was not started.

if args.mode == "record" or args.mode == "playback":
    print("Killing Servirtium Standalone Server")
    if args.mode == "record":
        subprocess.call(["docker", "cp", docker_container_name + ":Servirtium/test_recording_output/recording.md", ".compatibility_suite_recording.md"])
        print("Recording copied to: .compatibility_suite_recording.md")
    subprocess.call(["docker", "stop", docker_container_name])

print("Compatibility test suite completed. See above for pass/fail")