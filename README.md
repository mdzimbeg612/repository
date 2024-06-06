    # Cisco ISE dACL export/import
    #### Video Demo:  https://youtu.be/Dw_lGGkC1fY
    #### Description: Cisco ISE can't import or export dACL from GUI, but only through an API.
    #### You have to be ERS-Admin or Super Admin in ISE to be able to make API requests

    Export - When you make a GET request for dacl an ISE will give you 20 results by default. If you want more you must specify, but max is 100.
    If you have more than 100 you have to specify next page number to get next 100 results. When you have listed all of them, you now have only their IDs. Now you have to make API request for every ID seperately to get an actual ACL statement.

    Import - import is a simpler problem, but nevertheless you can't create/import many dACL at once. You have to do it one by one.

    I have made a script that can make import or export. You define it by arguments (-e, --export) and (-c, --create), where when doing an export you have to define format (1 or 2) and with import you have to define file from which to import data.
    Export format 1 is same format as file for import, while format 2 is made so that every acl statement in another line because this format will probably be needed if you want to import an acls in another system.

    After you start script with desired option it will ask you to input IP, Username and password (input of a password is hidden) of the Cisco ISE. Certificate warning is suppressed and script is printing count while getting all of the the dACLs when doing export. 
    So that user knows script is working and how far has come. Without that you see only cursor blinking and you don't know what is happening so user might interupt it because he is thinking that it stuck. 
    Especially if there are lot of dacl to export. And just in case at the end you will get message 'xxx dACL exported'.

    When doing an import, for easier troubleshoot, you will get number of line that is imported with API response. So if you get error answer like [500] you know for which line you got it.
    If you have a dACL in ISE with name of the one you want import you must first delete it from the ISE. API POST will not update it.

    If you don't specify any argument you will get message 'Too few command-line arguments' and if you specify more that one you will get 'Too many command-line arguments'. If you give argument without an option you will get message what you need to specify for that    argument.

    The script itself have:
    function (error) for error checking so in a case of an error you will get user friendly message.
    function (get_pages) that returns you how many number of pages there are.
    function (get_dacl_id) that goes through all of the pages and returns a list with all of the dacl IDs.
    function (get_dacl) that goes through a list of dACLs and makes list of dictionaries where every dict has {id: xx, name:yy, acl:zz}
    function (format1) that takes that list of dicts and saves data into a file in the desired format
    function (format2) that takes that list of dicts and saves data into a file in the desired format
    function (post) that imports data (creates dacl with a POST method) from specified file

    usage examples
    for format 1:   #python.exe ISE_dacl_export_import.py -e 1
    for format 2:   #python.exe ISE_dacl_export_import.py -e 2
    for import:     #python.exe ISE_dacl_export_import.py -c name_of_the_file_for_import.csv
