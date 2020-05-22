GBIF Norway is working with [DNV GL](https://www.dnvgl.com/contact/headquarters.html) to publish the species abundance data in the [MOD database](https://mod.dnvgl.com), on a yearly basis.

Data needs to be downloaded from MOD manually, and this script should be run with the resulting files.

## Downloading from MOD

1. Navigate to https://mod.dnvgl.com/
2. Log in (a username and password may need to be requested from DNV GL)
3. Export (left hand side menu) > Records export
4. Manually select the first dropdown (e.g. Barentshavet sør (X))
5. Open the javascript console in your browser (on chrome option + command + i)
6. Paste `var items = document.getElementsByTagName('input'); var first = items.length; Array.prototype.forEach.call(items, item => { item.click(); });`
7. Wait for it to finish running, then paste `nextItems = Array.prototype.slice.call(items, first); Array.prototype.forEach.call(nextItems, item => { item.click() });`
8. Download the Biology report type and Stations report type, save the files with the names suggested [here](https://github.com/gbif-norway/data-processing-dnv-gl/blob/master/script/script.py#L5)
10. Repeat steps 4 - 9 for the remaining dropdowns

## Converting from MOD data to DwC

1. Clone this project
2. Add the MOD files to the script/source_files folder
3. Run `docker-compose run script_service` to create and run the container, you will enter an interactive shell
4. Run `cd /srv/script` and then `python script.py`. The results should appear in script/result_files. 

Tests can be run using `python /srv/script/tests.py`.
