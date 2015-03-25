# Generate status of TOP github library registration

A number of scripts is provided to keep track of the progress of rehistering the top arduino libraries hostet on github.com

## mk-list-github.sh

Generates `list.github.top` by iterating through the search results of [https://github.com/search?o=desc&q=arduino+library+&ref=searchresults&s=stars&type=Repositories&utf8=%E2%9C%93'](arduino libraries by most stars)

This step requires quite some time, since it queries 100 pages and the queries are limites to 6 pages per minute. Best use it rarely.

## mk-list-platformio.sh

Generates `list.platformio.libs`, a list of all registered PlatformIO libraries utilising the PlatformIO Library Manager web API.

Use this script whenever the composition of registered libraries has changed. 

## mk-summary.sh

Generates TOP-libs-status.md and TOP-libs-TODO.md, containing tables of the overall status, and yet-to-be screened libraries, respectively.

This script uses `list.github.ignore` to mark certain search resukts as not to be considered for registration, optionally stating why the decision was made.

Search resupts that are neither registered as a library, nor marked to be not applicable, may be tagged with a state if work is in progress. This is done by searching the path `$HOME/prg/libs.%STATE%/` for a folder named like the repository on github. %STATE% can be any text and is used for the comment column if this folder exists.
Note that this only reflects the state of work of the last person committing the results of this script.
