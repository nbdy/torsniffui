# torsniffui
## a web ui for [torsniff](https://github.com/fanpei91/torsniff)
### install
```shell
pip3 install git+https://github.com/nbdy/torsniffui
```
### run
```shell
# this runs both torsniff and the ui in a docker container
./run.sh
```
### notes
#### add_watch: cannot watch WD=-1 (this will happen)
```shell
sudo sysctl -n -w fs.inotify.max_user_watches=65536
```