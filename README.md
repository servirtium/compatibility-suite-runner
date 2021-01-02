# Servirtium Compatibility Suite Runner

## Running this from a cloned/checked out directory

```
cd to/your/Servirtium/implementation/directory
./build.sh (or build.bat)
docker-compose build
python3 path/to/compatibility-suite-runner/compatibility-suite.py record -p 61417
```

## Running this GitHub without cloning

```
cd to/your/Servirtium/implementation/directory
./build.sh (or build.bat)
docker-compose build
# Mac and Linux:
curl -s https://raw.githubusercontent.com/servirtium/compatibility-suite-runner/main/compatibility-suite.py | python3 /dev/stdin record -p 61417
```