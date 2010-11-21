<?xml-stylesheet href="../htm/css/index.css" type="text/css"?>
#filter Filter
<response>
    <results >
        <name>$response.name</name>
        <description>$response.description</description>
    #for $resource in $response.resources:
    <resource >
        <name>$resource.name</name>
        <description>$resource.description</description>
        #for $argumentname in $resource.arguments:
        <arg>
            <name>$argumentname</name>
            <description>$resource.arguments[$argumentname]</description>
        </arg>
        #end for
    </resource>
    #end for
    </results>
#end filter
</response>
