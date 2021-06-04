## Components

There are 2 NSs, one for the static services i.e, the services that will always be up, and another one for the non-static services, the ones that will go down and up when needed.

## How to Run

To prepare the system, [OSM client](https://osm.etsi.org/wikipub/index.php/OSM_client) must be installed and updated and have a [VIM](https://osm.etsi.org/docs/user-guide/04-vim-setup.html) and [OSM](https://osm.etsi.org/) configured.

That said, the steps are as follows:

1. If you do not have the _tar.gz_ of each NS and VNF configuration directory, you need to do the following
   
     - For each NS and VNF configuration directory do the following
     
    ```
    $ tar -czvf <name_of_NS_or_VNF_configuration_directory>.tar.gz <name_of_NS_or_VNF_configuration_directory>/
    ```

    This will create the a single file with the collection of configuration files wrapped up in it
    
2. Do the onboarding of each VNF. To do this, do the following for each _tar.gz_ of the VNFs configuration files:
   
    ```
    $ osm vnfpkg-create <name_of_VNF_file_with_the_configuration>.tar.gz
    ```
    
3. Do the onboarding of each NS. To do this, do the following for each _tar.gz_ of the NSs configuration files:
    
    ```
    $ osm nsd-create <name_of_NS_file_with_the_configuration>.tar.gz
    ```
    
The NSs and VNFs should be onboarded on the OSM, now you can instanciate the NS through the user interface.

### Change configurations inside _tar.gz_

Just do `tar -xf <name_of_file_to_unpack_.tar.gz` to unpack the content, change what you need, and repeat the process above.


